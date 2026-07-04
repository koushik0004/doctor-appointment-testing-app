from __future__ import annotations

from copy import deepcopy
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.knowledge import KnowledgeDocument
from app.llm.models import (
    LLMCitation,
    LLMFinishReason,
    LLMGenerationConstraints,
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMMessage,
    LLMMessageRole,
    LLMReasoningConfig,
    LLMReasoningResult,
    LLMRequestedModality,
    LLMStreamingMetadata,
    LLMStreamingOptions,
    LLMStructuredOutputSchema,
    LLMTokenUsage,
    LLMToolCall,
    LLMToolChoice,
    LLMToolDefinition,
)
from app.llm.service import LLMIntegrationService
from app.services.prompt_builder import (
    PromptBuildRequest,
    PromptBuildResult,
    PromptBuilderService,
)


class LLMGenerationOrchestrationRequest(BaseModel):
    user_message: str = Field(min_length=1)
    conversation_state: dict[str, Any] = Field(default_factory=dict)
    documents: list[KnowledgeDocument] = Field(default_factory=list)
    active_intent: str | None = None
    system_instructions: list[str] = Field(default_factory=list)
    max_prompt_chars: int = Field(default=4000, gt=0)
    provider_name: str | None = None
    model_name: str | None = None
    constraints: LLMGenerationConstraints = Field(
        default_factory=LLMGenerationConstraints
    )
    requested_modalities: list[LLMRequestedModality] = Field(default_factory=list)
    structured_output: LLMStructuredOutputSchema | None = None
    tools: list[LLMToolDefinition] = Field(default_factory=list)
    tool_choice: LLMToolChoice | None = None
    reasoning: LLMReasoningConfig | None = None
    streaming: LLMStreamingOptions = Field(default_factory=LLMStreamingOptions)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class LLMGenerationOrchestrationResult(BaseModel):
    prompt: str = Field(min_length=1)
    prompt_blocks: list[dict[str, Any]] = Field(default_factory=list)
    prompt_truncated: bool = False
    included_document_ids: list[str] = Field(default_factory=list)
    excluded_document_ids: list[str] = Field(default_factory=list)
    requires_domain_validation: bool = False
    response_message: LLMMessage
    finish_reason: LLMFinishReason = LLMFinishReason.STOP
    provider_name: str | None = None
    model_name: str | None = None
    usage: LLMTokenUsage | None = None
    structured_output: dict[str, Any] | None = None
    tool_calls: list[LLMToolCall] = Field(default_factory=list)
    reasoning: LLMReasoningResult | None = None
    streaming: LLMStreamingMetadata | None = None
    citations: list[LLMCitation] = Field(default_factory=list)
    provider_metadata: dict[str, Any] = Field(default_factory=dict)
    model_metadata: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMGenerationOrchestrator:
    """Inactive coordinator between Prompt Builder and LLM integration."""

    def __init__(
        self,
        *,
        prompt_builder: PromptBuilderService | None = None,
        llm_integration_service: LLMIntegrationService | None = None,
    ) -> None:
        self._prompt_builder = (
            prompt_builder if prompt_builder is not None else PromptBuilderService()
        )
        self._llm_integration_service = (
            llm_integration_service
            if llm_integration_service is not None
            else LLMIntegrationService()
        )

    def generate(
        self,
        request: LLMGenerationOrchestrationRequest,
    ) -> LLMGenerationOrchestrationResult:
        prompt_result = self._prompt_builder.build(self._build_prompt_request(request))
        llm_request = self.build_llm_request(request, prompt_result=prompt_result)
        llm_response = self._llm_integration_service.generate(
            llm_request,
            provider_name=request.provider_name,
        )
        return self._normalize_result(prompt_result=prompt_result, response=llm_response)

    def build_llm_request(
        self,
        request: LLMGenerationOrchestrationRequest,
        *,
        prompt_result: PromptBuildResult,
    ) -> LLMGenerationRequest:
        prompt_metadata = {
            "included_document_ids": list(prompt_result.included_document_ids),
            "excluded_document_ids": list(prompt_result.excluded_document_ids),
            "truncated": prompt_result.truncated,
            "requires_domain_validation": prompt_result.requires_domain_validation,
            "block_count": len(prompt_result.blocks),
        }

        metadata = deepcopy(request.metadata)
        metadata.setdefault("orchestration", {})
        metadata["orchestration"] = {
            **prompt_metadata,
            **deepcopy(metadata["orchestration"]),
        }

        return LLMGenerationRequest(
            messages=[
                LLMMessage(
                    role=LLMMessageRole.USER,
                    content=prompt_result.prompt,
                    metadata={
                        "source": "prompt_builder",
                        "block_count": len(prompt_result.blocks),
                    },
                )
            ],
            prompt=prompt_result.prompt,
            model_name=request.model_name,
            constraints=deepcopy(request.constraints),
            requested_modalities=list(request.requested_modalities),
            structured_output=deepcopy(request.structured_output),
            tools=deepcopy(request.tools),
            tool_choice=deepcopy(request.tool_choice),
            reasoning=deepcopy(request.reasoning),
            streaming=deepcopy(request.streaming),
            metadata=metadata,
        )

    def _build_prompt_request(
        self,
        request: LLMGenerationOrchestrationRequest,
    ) -> PromptBuildRequest:
        return PromptBuildRequest(
            user_message=request.user_message,
            conversation_state=deepcopy(request.conversation_state),
            documents=list(request.documents),
            active_intent=request.active_intent,
            system_instructions=list(request.system_instructions),
            max_prompt_chars=request.max_prompt_chars,
        )

    def _normalize_result(
        self,
        *,
        prompt_result: PromptBuildResult,
        response: LLMGenerationResponse,
    ) -> LLMGenerationOrchestrationResult:
        return LLMGenerationOrchestrationResult(
            prompt=prompt_result.prompt,
            prompt_blocks=[block.model_dump(mode="json") for block in prompt_result.blocks],
            prompt_truncated=prompt_result.truncated,
            included_document_ids=list(prompt_result.included_document_ids),
            excluded_document_ids=list(prompt_result.excluded_document_ids),
            requires_domain_validation=prompt_result.requires_domain_validation,
            response_message=response.message,
            finish_reason=response.finish_reason,
            provider_name=response.provider_name,
            model_name=response.model_name,
            usage=response.usage,
            structured_output=deepcopy(response.structured_output),
            tool_calls=deepcopy(response.tool_calls),
            reasoning=deepcopy(response.reasoning),
            streaming=deepcopy(response.streaming),
            citations=deepcopy(response.citations),
            provider_metadata=deepcopy(response.provider_metadata),
            model_metadata=deepcopy(response.model_metadata),
            metadata=deepcopy(response.metadata),
        )
