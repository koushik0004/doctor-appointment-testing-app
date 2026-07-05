from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Protocol

from app.llm.adapters import BaseLLMProviderAdapter
from app.llm.config import LLMConfiguration, LLMProviderConfiguration, LLMProviderName
from app.llm.models import (
    LLMFinishReason,
    LLMGenerationRequest,
    LLMGenerationResponse,
    LLMMessage,
    LLMMessageRole,
    LLMProviderCapabilities,
    LLMProviderDescriptor,
    LLMReasoningResult,
    LLMStructuredOutputMode,
    LLMTokenUsage,
    LLMToolCall,
)
from app.llm.registry import InMemoryLLMProviderRegistry


ProviderPayload = dict[str, Any]


class LLMProviderTransport(Protocol):
    """Explicit inactive transport seam for concrete provider adapters."""

    def invoke(self, request: ProviderPayload) -> ProviderPayload:
        ...


class ConfigurableLLMProviderAdapter(
    BaseLLMProviderAdapter[ProviderPayload, ProviderPayload],
    ABC,
):
    provider_name: LLMProviderName

    def __init__(
        self,
        configuration: LLMProviderConfiguration,
        *,
        transport: LLMProviderTransport | None = None,
    ) -> None:
        if configuration.provider_name is not self.provider_name:
            raise ValueError(
                "Provider configuration does not match adapter type: "
                f"expected '{self.provider_name.value}', "
                f"received '{configuration.provider_name.value}'."
            )

        self._configuration = configuration
        self._transport = transport

    def describe(self) -> LLMProviderDescriptor:
        return LLMProviderDescriptor(
            provider_name=self.provider_name.value,
            default_model_name=self._configuration.default_model_name,
            capabilities=self._build_capabilities(),
            metadata={
                "enabled": self._configuration.enabled,
                "base_url_configured": self._configuration.base_url is not None,
                "generation_budget_default_profile": (
                    self._configuration.generation_budget_profiles.default_profile.value
                ),
            },
        )

    def invoke_provider(self, request: ProviderPayload) -> ProviderPayload:
        if self._transport is None:
            raise RuntimeError(
                f"{self.provider_name.value} adapter is inactive: no provider transport is configured."
            )
        return self._transport.invoke(request)

    def _build_capabilities(self) -> LLMProviderCapabilities:
        feature_flags = self._configuration.feature_flags
        return LLMProviderCapabilities(
            supports_system_prompt=True,
            supports_message_history=True,
            supports_streaming=feature_flags.streaming,
            supports_json_output=feature_flags.structured_output,
            supports_tool_calls=feature_flags.tool_calls,
            supports_reasoning=feature_flags.reasoning,
            supports_citations=feature_flags.citations,
        )

    def _resolve_model_name(self, request: LLMGenerationRequest) -> str:
        model_name = request.model_name or self._configuration.default_model_name
        if model_name is None:
            raise RuntimeError(
                f"{self.provider_name.value} adapter requires a model name in the request or configuration."
            )
        return model_name

    def _translate_messages(
        self,
        messages: list[LLMMessage],
    ) -> list[dict[str, Any]]:
        return [self._translate_message(message) for message in messages]

    def _translate_message(self, message: LLMMessage) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "role": message.role.value,
            "content": message.content,
        }
        if message.name is not None:
            payload["name"] = message.name
        if message.tool_call_id is not None:
            payload["tool_call_id"] = message.tool_call_id
        if message.tool_calls:
            payload["tool_calls"] = [
                {
                    "id": tool_call.call_id,
                    "name": tool_call.tool_name,
                    "arguments": dict(tool_call.arguments),
                    "metadata": dict(tool_call.metadata),
                }
                for tool_call in message.tool_calls
            ]
        if message.metadata:
            payload["metadata"] = dict(message.metadata)
        return payload

    def _translate_tools(self, request: LLMGenerationRequest) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": dict(tool.input_schema),
                "metadata": dict(tool.metadata),
            }
            for tool in request.tools
        ]

    def _translate_tool_choice(
        self,
        request: LLMGenerationRequest,
    ) -> dict[str, Any] | None:
        if request.tool_choice is None:
            return None

        payload = {"mode": request.tool_choice.mode.value}
        if request.tool_choice.tool_name is not None:
            payload["tool_name"] = request.tool_choice.tool_name
        if request.tool_choice.metadata:
            payload["metadata"] = dict(request.tool_choice.metadata)
        return payload

    def _translate_structured_output(
        self,
        request: LLMGenerationRequest,
    ) -> dict[str, Any] | None:
        if request.structured_output is None:
            return None

        payload = {
            "mode": request.structured_output.mode.value,
            "strict": request.structured_output.strict,
            "metadata": dict(request.structured_output.metadata),
        }
        if request.structured_output.name is not None:
            payload["name"] = request.structured_output.name
        if request.structured_output.schema_definition is not None:
            payload["schema"] = dict(request.structured_output.schema_definition)
        return payload

    def _translate_reasoning(
        self,
        request: LLMGenerationRequest,
    ) -> dict[str, Any] | None:
        if request.reasoning is None:
            return None

        payload = {
            "include_summary": request.reasoning.include_summary,
            "metadata": dict(request.reasoning.metadata),
        }
        if request.reasoning.effort is not None:
            payload["effort"] = request.reasoning.effort.value
        return payload

    def _translate_budget(
        self,
        request: LLMGenerationRequest,
    ) -> dict[str, Any] | None:
        if request.generation_budget is None:
            return None
        return self.translate_generation_budget(request.generation_budget)

    def _translate_common_request_metadata(
        self,
        request: LLMGenerationRequest,
    ) -> dict[str, Any]:
        return {
            "prompt": request.prompt,
            "system_prompt": request.system_prompt,
            "requested_modalities": [modality.value for modality in request.requested_modalities],
            "streaming": {
                "enabled": request.streaming.enabled,
                "include_usage": request.streaming.include_usage,
                "metadata": dict(request.streaming.metadata),
            },
            "metadata": dict(request.metadata),
        }

    def _translate_finish_reason(
        self,
        raw_reason: str | None,
        *,
        mapping: Mapping[str, LLMFinishReason] | None = None,
    ) -> LLMFinishReason:
        if raw_reason is None:
            return LLMFinishReason.STOP

        normalized = raw_reason.strip().lower()
        if mapping is not None and normalized in mapping:
            return mapping[normalized]
        if normalized in {"stop", "end_turn", "complete", "completed", "done"}:
            return LLMFinishReason.STOP
        if normalized in {"length", "max_tokens", "max_output_tokens"}:
            return LLMFinishReason.LENGTH
        if normalized in {"tool_call", "tool_calls", "function_call"}:
            return LLMFinishReason.TOOL_CALL
        if normalized in {"content_filter", "safety"}:
            return LLMFinishReason.CONTENT_FILTER
        return LLMFinishReason.OTHER

    def _translate_tool_calls_from_response(
        self,
        response: ProviderPayload,
        *,
        key: str = "tool_calls",
        id_key: str = "id",
        name_key: str = "name",
        arguments_key: str = "arguments",
    ) -> list[LLMToolCall]:
        raw_calls = response.get(key)
        if not isinstance(raw_calls, list):
            return []

        tool_calls: list[LLMToolCall] = []
        for index, raw_call in enumerate(raw_calls):
            if not isinstance(raw_call, dict):
                continue
            tool_calls.append(
                LLMToolCall(
                    call_id=str(raw_call.get(id_key) or f"tool-call-{index}"),
                    tool_name=str(raw_call.get(name_key) or "unknown_tool"),
                    arguments=(
                        dict(raw_call.get(arguments_key))
                        if isinstance(raw_call.get(arguments_key), dict)
                        else {}
                    ),
                    metadata=(
                        dict(raw_call.get("metadata"))
                        if isinstance(raw_call.get("metadata"), dict)
                        else {}
                    ),
                )
            )
        return tool_calls

    def _translate_usage(
        self,
        *,
        input_tokens: int | None,
        output_tokens: int | None,
        total_tokens: int | None = None,
    ) -> LLMTokenUsage | None:
        if input_tokens is None and output_tokens is None and total_tokens is None:
            return None

        resolved_total = total_tokens
        if resolved_total is None and input_tokens is not None and output_tokens is not None:
            resolved_total = input_tokens + output_tokens

        return LLMTokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=resolved_total,
        )

    @abstractmethod
    def translate_generation_budget(self, budget) -> dict[str, Any]:
        ...


class OpenAICompatibleProviderAdapter(ConfigurableLLMProviderAdapter, ABC):
    def translate_request(self, request: LLMGenerationRequest) -> ProviderPayload:
        payload: ProviderPayload = {
            "model": self._resolve_model_name(request),
            "messages": self._translate_messages(request.messages),
            "stream": request.streaming.enabled,
            "adapter_metadata": self._translate_common_request_metadata(request),
        }
        if request.constraints.max_output_tokens is not None:
            payload["max_completion_tokens"] = request.constraints.max_output_tokens
        if request.constraints.temperature is not None:
            payload["temperature"] = request.constraints.temperature
        if request.constraints.top_p is not None:
            payload["top_p"] = request.constraints.top_p
        if request.constraints.stop_sequences:
            payload["stop"] = list(request.constraints.stop_sequences)
        if request.system_prompt is not None:
            payload["system"] = request.system_prompt

        response_format = self._translate_structured_output(request)
        if response_format is not None:
            payload["response_format"] = response_format

        tools = self._translate_tools(request)
        if tools:
            payload["tools"] = tools

        tool_choice = self._translate_tool_choice(request)
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice

        reasoning = self._translate_reasoning(request)
        if reasoning is not None:
            payload["reasoning"] = reasoning

        generation_budget = self._translate_budget(request)
        if generation_budget is not None:
            payload["generation_budget"] = generation_budget

        return payload

    def translate_response(
        self,
        response: ProviderPayload,
        *,
        request: LLMGenerationRequest,
    ) -> LLMGenerationResponse:
        usage_payload = response.get("usage")
        usage = None
        if isinstance(usage_payload, dict):
            usage = self._translate_usage(
                input_tokens=usage_payload.get("prompt_tokens"),
                output_tokens=usage_payload.get("completion_tokens"),
                total_tokens=usage_payload.get("total_tokens"),
            )

        return LLMGenerationResponse(
            message=LLMMessage(
                role=LLMMessageRole.ASSISTANT,
                content=str(response.get("content") or ""),
            ),
            finish_reason=self._translate_finish_reason(
                response.get("finish_reason"),
            ),
            model_name=str(response.get("model")) if response.get("model") else None,
            usage=usage,
            structured_output=(
                dict(response.get("structured_output"))
                if isinstance(response.get("structured_output"), dict)
                else None
            ),
            tool_calls=self._translate_tool_calls_from_response(response),
            reasoning=(
                LLMReasoningResult(
                    effort=request.reasoning.effort if request.reasoning else None,
                    summary=str(response.get("reasoning_summary")),
                )
                if response.get("reasoning_summary") is not None
                else None
            ),
            provider_metadata=(
                dict(response.get("provider_metadata"))
                if isinstance(response.get("provider_metadata"), dict)
                else {}
            ),
            model_metadata=(
                dict(response.get("model_metadata"))
                if isinstance(response.get("model_metadata"), dict)
                else {}
            ),
            metadata=(
                dict(response.get("metadata"))
                if isinstance(response.get("metadata"), dict)
                else {}
            ),
        )


class OpenAIProviderAdapter(OpenAICompatibleProviderAdapter):
    provider_name = LLMProviderName.OPENAI

    def translate_generation_budget(self, budget) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if budget.reasoning_effort is not None:
            payload["reasoning_effort"] = budget.reasoning_effort.value
        if budget.max_output_tokens is not None:
            payload["max_completion_tokens"] = budget.max_output_tokens
        if budget.max_context_tokens is not None:
            payload["context_window_tokens"] = budget.max_context_tokens
        if budget.latency_preference is not None:
            payload["latency_tier"] = budget.latency_preference.value
        if budget.quality_preference is not None:
            payload["quality_tier"] = budget.quality_preference.value
        if budget.cost_preference is not None:
            payload["cost_tier"] = budget.cost_preference.value
        if budget.profile is not None:
            payload["profile"] = budget.profile.value
        if budget.metadata:
            payload["metadata"] = dict(budget.metadata)
        return payload


class OpenRouterProviderAdapter(OpenAICompatibleProviderAdapter):
    provider_name = LLMProviderName.OPENROUTER

    def translate_generation_budget(self, budget) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if budget.reasoning_effort is not None:
            payload["reasoning"] = {"effort": budget.reasoning_effort.value}
        if budget.max_output_tokens is not None:
            payload["max_tokens"] = budget.max_output_tokens
        if budget.max_context_tokens is not None:
            payload["context_window_tokens"] = budget.max_context_tokens
        if budget.latency_preference is not None:
            payload["provider_routing"] = {"latency": budget.latency_preference.value}
        if budget.quality_preference is not None:
            payload["quality_hint"] = budget.quality_preference.value
        if budget.cost_preference is not None:
            payload["cost_hint"] = budget.cost_preference.value
        if budget.profile is not None:
            payload["profile"] = budget.profile.value
        if budget.metadata:
            payload["metadata"] = dict(budget.metadata)
        return payload


class ClaudeProviderAdapter(ConfigurableLLMProviderAdapter):
    provider_name = LLMProviderName.CLAUDE

    def translate_request(self, request: LLMGenerationRequest) -> ProviderPayload:
        payload: ProviderPayload = {
            "model": self._resolve_model_name(request),
            "messages": self._translate_messages(request.messages),
            "adapter_metadata": self._translate_common_request_metadata(request),
        }
        if request.system_prompt is not None:
            payload["system"] = request.system_prompt
        if request.constraints.max_output_tokens is not None:
            payload["max_tokens"] = request.constraints.max_output_tokens
        if request.constraints.temperature is not None:
            payload["temperature"] = request.constraints.temperature
        if request.constraints.top_p is not None:
            payload["top_p"] = request.constraints.top_p
        if request.constraints.stop_sequences:
            payload["stop_sequences"] = list(request.constraints.stop_sequences)

        structured_output = self._translate_structured_output(request)
        if structured_output is not None:
            payload["output_schema"] = structured_output

        tools = self._translate_tools(request)
        if tools:
            payload["tools"] = tools

        tool_choice = self._translate_tool_choice(request)
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice

        reasoning = self._translate_reasoning(request)
        if reasoning is not None:
            payload["thinking"] = reasoning

        generation_budget = self._translate_budget(request)
        if generation_budget is not None:
            payload["generation_budget"] = generation_budget

        return payload

    def translate_response(
        self,
        response: ProviderPayload,
        *,
        request: LLMGenerationRequest,
    ) -> LLMGenerationResponse:
        usage_payload = response.get("usage")
        usage = None
        if isinstance(usage_payload, dict):
            usage = self._translate_usage(
                input_tokens=usage_payload.get("input_tokens"),
                output_tokens=usage_payload.get("output_tokens"),
            )

        return LLMGenerationResponse(
            message=LLMMessage(
                role=LLMMessageRole.ASSISTANT,
                content=str(response.get("content") or ""),
            ),
            finish_reason=self._translate_finish_reason(
                response.get("stop_reason"),
                mapping={"end_turn": LLMFinishReason.STOP},
            ),
            model_name=str(response.get("model")) if response.get("model") else None,
            usage=usage,
            structured_output=(
                dict(response.get("structured_output"))
                if isinstance(response.get("structured_output"), dict)
                else None
            ),
            tool_calls=self._translate_tool_calls_from_response(
                response,
                id_key="tool_use_id",
                name_key="tool_name",
            ),
            reasoning=(
                LLMReasoningResult(
                    effort=request.reasoning.effort if request.reasoning else None,
                    summary=str(response.get("thinking_summary")),
                )
                if response.get("thinking_summary") is not None
                else None
            ),
            provider_metadata=(
                dict(response.get("provider_metadata"))
                if isinstance(response.get("provider_metadata"), dict)
                else {}
            ),
            model_metadata=(
                dict(response.get("model_metadata"))
                if isinstance(response.get("model_metadata"), dict)
                else {}
            ),
            metadata=(
                dict(response.get("metadata"))
                if isinstance(response.get("metadata"), dict)
                else {}
            ),
        )

    def translate_generation_budget(self, budget) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if budget.reasoning_effort is not None:
            payload["thinking"] = {"effort": budget.reasoning_effort.value}
        if budget.max_output_tokens is not None:
            payload["max_tokens"] = budget.max_output_tokens
        if budget.max_context_tokens is not None:
            payload["context_management"] = {
                "max_input_tokens": budget.max_context_tokens
            }
        if budget.latency_preference is not None:
            payload["latency_preference"] = budget.latency_preference.value
        if budget.quality_preference is not None:
            payload["quality_preference"] = budget.quality_preference.value
        if budget.cost_preference is not None:
            payload["cost_preference"] = budget.cost_preference.value
        if budget.profile is not None:
            payload["profile"] = budget.profile.value
        if budget.metadata:
            payload["metadata"] = dict(budget.metadata)
        return payload


class GeminiProviderAdapter(ConfigurableLLMProviderAdapter):
    provider_name = LLMProviderName.GEMINI

    def translate_request(self, request: LLMGenerationRequest) -> ProviderPayload:
        payload: ProviderPayload = {
            "model": self._resolve_model_name(request),
            "contents": self._translate_messages(request.messages),
            "adapter_metadata": self._translate_common_request_metadata(request),
        }
        if request.system_prompt is not None:
            payload["system_instruction"] = request.system_prompt

        generation_config: dict[str, Any] = {}
        if request.constraints.max_output_tokens is not None:
            generation_config["max_output_tokens"] = request.constraints.max_output_tokens
        if request.constraints.temperature is not None:
            generation_config["temperature"] = request.constraints.temperature
        if request.constraints.top_p is not None:
            generation_config["top_p"] = request.constraints.top_p
        if request.constraints.stop_sequences:
            generation_config["stop_sequences"] = list(request.constraints.stop_sequences)
        if generation_config:
            payload["generation_config"] = generation_config

        structured_output = self._translate_structured_output(request)
        if structured_output is not None:
            payload["response_schema"] = structured_output

        tools = self._translate_tools(request)
        if tools:
            payload["tools"] = tools

        tool_choice = self._translate_tool_choice(request)
        if tool_choice is not None:
            payload["tool_config"] = tool_choice

        reasoning = self._translate_reasoning(request)
        if reasoning is not None:
            payload["thinking_config"] = reasoning

        generation_budget = self._translate_budget(request)
        if generation_budget is not None:
            payload["generation_budget"] = generation_budget

        return payload

    def translate_response(
        self,
        response: ProviderPayload,
        *,
        request: LLMGenerationRequest,
    ) -> LLMGenerationResponse:
        usage_payload = response.get("usage_metadata")
        usage = None
        if isinstance(usage_payload, dict):
            usage = self._translate_usage(
                input_tokens=usage_payload.get("prompt_token_count"),
                output_tokens=usage_payload.get("candidates_token_count"),
                total_tokens=usage_payload.get("total_token_count"),
            )

        raw_content = response.get("content")
        message_content = raw_content if isinstance(raw_content, str) else response.get("text")

        return LLMGenerationResponse(
            message=LLMMessage(
                role=LLMMessageRole.ASSISTANT,
                content=str(message_content or ""),
            ),
            finish_reason=self._translate_finish_reason(response.get("finish_reason")),
            model_name=str(response.get("model")) if response.get("model") else None,
            usage=usage,
            structured_output=(
                dict(response.get("structured_output"))
                if isinstance(response.get("structured_output"), dict)
                else None
            ),
            tool_calls=self._translate_tool_calls_from_response(
                response,
                id_key="call_id",
                name_key="name",
            ),
            reasoning=(
                LLMReasoningResult(
                    effort=request.reasoning.effort if request.reasoning else None,
                    summary=str(response.get("thinking_summary")),
                )
                if response.get("thinking_summary") is not None
                else None
            ),
            provider_metadata=(
                dict(response.get("provider_metadata"))
                if isinstance(response.get("provider_metadata"), dict)
                else {}
            ),
            model_metadata=(
                dict(response.get("model_metadata"))
                if isinstance(response.get("model_metadata"), dict)
                else {}
            ),
            metadata=(
                dict(response.get("metadata"))
                if isinstance(response.get("metadata"), dict)
                else {}
            ),
        )

    def translate_generation_budget(self, budget) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if budget.reasoning_effort is not None:
            payload["thinking_config"] = {"effort": budget.reasoning_effort.value}
        if budget.max_output_tokens is not None:
            payload["generation_config"] = {"max_output_tokens": budget.max_output_tokens}
        if budget.max_context_tokens is not None:
            payload["context_window_tokens"] = budget.max_context_tokens
        if budget.latency_preference is not None:
            payload["latency_hint"] = budget.latency_preference.value
        if budget.quality_preference is not None:
            payload["quality_hint"] = budget.quality_preference.value
        if budget.cost_preference is not None:
            payload["cost_hint"] = budget.cost_preference.value
        if budget.profile is not None:
            payload["profile"] = budget.profile.value
        if budget.metadata:
            payload["metadata"] = dict(budget.metadata)
        return payload


class OllamaProviderAdapter(ConfigurableLLMProviderAdapter):
    provider_name = LLMProviderName.OLLAMA

    def translate_request(self, request: LLMGenerationRequest) -> ProviderPayload:
        options: dict[str, Any] = {}
        if request.constraints.temperature is not None:
            options["temperature"] = request.constraints.temperature
        if request.constraints.top_p is not None:
            options["top_p"] = request.constraints.top_p
        if request.constraints.max_output_tokens is not None:
            options["num_predict"] = request.constraints.max_output_tokens
        if request.generation_budget is not None:
            budget_payload = self.translate_generation_budget(request.generation_budget)
            if isinstance(budget_payload.get("options"), dict):
                options.update(dict(budget_payload["options"]))

        payload: ProviderPayload = {
            "model": self._resolve_model_name(request),
            "messages": self._translate_messages(request.messages),
            "stream": request.streaming.enabled,
            "adapter_metadata": self._translate_common_request_metadata(request),
        }
        if request.system_prompt is not None:
            payload["system"] = request.system_prompt
        if request.constraints.stop_sequences:
            payload["stop"] = list(request.constraints.stop_sequences)
        if options:
            payload["options"] = options

        structured_output = self._translate_structured_output(request)
        if structured_output is not None:
            payload["format"] = (
                "json"
                if structured_output["mode"] == LLMStructuredOutputMode.JSON_OBJECT.value
                else structured_output
            )

        tools = self._translate_tools(request)
        if tools:
            payload["tools"] = tools

        return payload

    def translate_response(
        self,
        response: ProviderPayload,
        *,
        request: LLMGenerationRequest,
    ) -> LLMGenerationResponse:
        raw_message = response.get("message")
        content = ""
        if isinstance(raw_message, dict):
            content = str(raw_message.get("content") or "")
        elif response.get("content") is not None:
            content = str(response.get("content"))

        return LLMGenerationResponse(
            message=LLMMessage(role=LLMMessageRole.ASSISTANT, content=content),
            finish_reason=self._translate_finish_reason(response.get("done_reason")),
            model_name=str(response.get("model")) if response.get("model") else None,
            usage=self._translate_usage(
                input_tokens=response.get("prompt_eval_count"),
                output_tokens=response.get("eval_count"),
            ),
            structured_output=(
                dict(response.get("structured_output"))
                if isinstance(response.get("structured_output"), dict)
                else None
            ),
            tool_calls=self._translate_tool_calls_from_response(response),
            reasoning=(
                LLMReasoningResult(
                    summary=str(response.get("reasoning_summary")),
                )
                if response.get("reasoning_summary") is not None
                else None
            ),
            provider_metadata=(
                dict(response.get("provider_metadata"))
                if isinstance(response.get("provider_metadata"), dict)
                else {}
            ),
            model_metadata=(
                dict(response.get("model_metadata"))
                if isinstance(response.get("model_metadata"), dict)
                else {}
            ),
            metadata=(
                dict(response.get("metadata"))
                if isinstance(response.get("metadata"), dict)
                else {}
            ),
        )

    def translate_generation_budget(self, budget) -> dict[str, Any]:
        options: dict[str, Any] = {}
        if budget.max_output_tokens is not None:
            options["num_predict"] = budget.max_output_tokens
        if budget.max_context_tokens is not None:
            options["num_ctx"] = budget.max_context_tokens
        if budget.reasoning_effort is not None:
            options["reasoning_effort"] = budget.reasoning_effort.value

        payload: dict[str, Any] = {}
        if options:
            payload["options"] = options
        if budget.latency_preference is not None:
            payload["latency_hint"] = budget.latency_preference.value
        if budget.quality_preference is not None:
            payload["quality_hint"] = budget.quality_preference.value
        if budget.cost_preference is not None:
            payload["cost_hint"] = budget.cost_preference.value
        if budget.profile is not None:
            payload["profile"] = budget.profile.value
        if budget.metadata:
            payload["metadata"] = dict(budget.metadata)
        return payload


class LLMProviderAdapterFactory:
    """Explicit inactive factory for concrete provider adapters."""

    _adapter_types = {
        LLMProviderName.OPENAI: OpenAIProviderAdapter,
        LLMProviderName.CLAUDE: ClaudeProviderAdapter,
        LLMProviderName.GEMINI: GeminiProviderAdapter,
        LLMProviderName.OPENROUTER: OpenRouterProviderAdapter,
        LLMProviderName.OLLAMA: OllamaProviderAdapter,
    }

    def create_adapter(
        self,
        configuration: LLMProviderConfiguration,
        *,
        transport: LLMProviderTransport | None = None,
    ) -> ConfigurableLLMProviderAdapter:
        adapter_type = self._adapter_types[configuration.provider_name]
        return adapter_type(configuration, transport=transport)

    def create_registry(
        self,
        configuration: LLMConfiguration,
        *,
        transports: Mapping[str, LLMProviderTransport] | None = None,
        default_provider_name: str | None = None,
    ) -> InMemoryLLMProviderRegistry:
        providers = []
        for provider_config in configuration.providers:
            if not provider_config.enabled:
                continue
            provider_transport = None
            if transports is not None:
                provider_transport = transports.get(provider_config.provider_name.value)
            providers.append(
                self.create_adapter(
                    provider_config,
                    transport=provider_transport,
                )
            )

        resolved_default = default_provider_name
        if (
            resolved_default is None
            and configuration.selected_provider_name is not None
            and configuration.get_provider(configuration.selected_provider_name) is not None
            and configuration.get_provider(configuration.selected_provider_name).enabled
        ):
            resolved_default = configuration.selected_provider_name.value

        return InMemoryLLMProviderRegistry(
            providers,
            default_provider_name=resolved_default,
        )
