from __future__ import annotations

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.knowledge import KnowledgeDocument


class PromptContextBlockKind(str, Enum):
    USER_MESSAGE = "user_message"
    CONVERSATION_STATE = "conversation_state"
    KNOWLEDGE_DOCUMENT = "knowledge_document"


class PromptContextBlock(BaseModel):
    kind: PromptContextBlockKind
    label: str = Field(min_length=1)
    content: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptContextMetadata(BaseModel):
    active_intent: str | None = None
    included_document_ids: list[str] = Field(default_factory=list)
    excluded_document_ids: list[str] = Field(default_factory=list)
    requires_domain_validation: bool = False

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptContextUserContext(BaseModel):
    message: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptContextConversationContext(BaseModel):
    state: dict[str, Any] = Field(default_factory=dict)


class PromptContextWorkflowContext(BaseModel):
    active_intent: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptContextKnowledgeDocument(BaseModel):
    document_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    audience: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    content: str | dict[str, Any]
    safe_to_quote: bool = False
    requires_domain_validation: bool = False
    max_context_chars: int | None = Field(default=None, gt=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptContextKnowledgeContext(BaseModel):
    documents: list[PromptContextKnowledgeDocument] = Field(default_factory=list)


class PromptContextSystemInstructions(BaseModel):
    instructions: list[str] = Field(default_factory=list)

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptContextConstraints(BaseModel):
    max_prompt_chars: int = Field(default=4000, gt=0)


class PromptContextRenderingOptions(BaseModel):
    include_section_headers: bool = True
    json_sort_keys: bool = True
    json_ensure_ascii: bool = True
    json_compact: bool = True
    truncation_marker: str = Field(default="[TRUNCATED]", min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptContext(BaseModel):
    metadata: PromptContextMetadata = Field(default_factory=PromptContextMetadata)
    user_context: PromptContextUserContext
    conversation_context: PromptContextConversationContext | None = None
    workflow_context: PromptContextWorkflowContext | None = None
    knowledge_context: PromptContextKnowledgeContext | None = None
    system_instructions: PromptContextSystemInstructions = Field(
        default_factory=PromptContextSystemInstructions
    )
    constraints: PromptContextConstraints = Field(default_factory=PromptContextConstraints)
    rendering_options: PromptContextRenderingOptions = Field(
        default_factory=PromptContextRenderingOptions
    )


class PromptBuildRequest(BaseModel):
    user_message: str = Field(min_length=1)
    conversation_state: dict[str, Any] = Field(default_factory=dict)
    documents: list[KnowledgeDocument] = Field(default_factory=list)
    active_intent: str | None = None
    system_instructions: list[str] = Field(default_factory=list)
    max_prompt_chars: int = Field(default=4000, gt=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptBuildResult(BaseModel):
    prompt: str = Field(min_length=1)
    blocks: list[PromptContextBlock] = Field(default_factory=list)
    included_document_ids: list[str] = Field(default_factory=list)
    excluded_document_ids: list[str] = Field(default_factory=list)
    truncated: bool = False
    requires_domain_validation: bool = False


class PromptBuilderService:
    """Deterministically formats already-selected context into prompt text."""

    def build(self, request: PromptBuildRequest) -> PromptBuildResult:
        context = self.build_context(request)
        blocks = self._build_blocks(context)

        prompt, truncated = self._compose_prompt(
            blocks=blocks,
            context=context,
        )

        return PromptBuildResult(
            prompt=prompt,
            blocks=blocks,
            included_document_ids=context.metadata.included_document_ids,
            excluded_document_ids=context.metadata.excluded_document_ids,
            truncated=truncated,
            requires_domain_validation=context.metadata.requires_domain_validation,
        )

    def build_context(self, request: PromptBuildRequest) -> PromptContext:
        included_documents: list[PromptContextKnowledgeDocument] = []
        included_document_ids: list[str] = []
        excluded_document_ids: list[str] = []
        requires_domain_validation = False

        for document in request.documents:
            if not self._should_include_document(document, request.active_intent):
                excluded_document_ids.append(document.id)
                continue

            context_document = self._to_context_document(document)
            included_documents.append(context_document)
            included_document_ids.append(document.id)
            if context_document.requires_domain_validation:
                requires_domain_validation = True

        return PromptContext(
            metadata=PromptContextMetadata(
                active_intent=request.active_intent,
                included_document_ids=included_document_ids,
                excluded_document_ids=excluded_document_ids,
                requires_domain_validation=requires_domain_validation,
            ),
            user_context=PromptContextUserContext(message=request.user_message),
            conversation_context=(
                PromptContextConversationContext(state=request.conversation_state)
                if request.conversation_state
                else None
            ),
            workflow_context=(
                PromptContextWorkflowContext(active_intent=request.active_intent)
                if request.active_intent
                else None
            ),
            knowledge_context=(
                PromptContextKnowledgeContext(documents=included_documents)
                if included_documents
                else None
            ),
            system_instructions=PromptContextSystemInstructions(
                instructions=list(request.system_instructions)
            ),
            constraints=PromptContextConstraints(max_prompt_chars=request.max_prompt_chars),
        )

    def _should_include_document(self, document: KnowledgeDocument, active_intent: str | None) -> bool:
        hints = document.prompt_hints
        if hints is None or active_intent is None:
            return True

        if active_intent in hints.exclude_when_intents:
            return False
        if hints.include_when_intents and active_intent not in hints.include_when_intents:
            return False
        return True

    def _to_context_document(self, document: KnowledgeDocument) -> PromptContextKnowledgeDocument:
        hints = document.prompt_hints
        return PromptContextKnowledgeDocument(
            document_id=document.id,
            title=document.title,
            source_path=document.source_path,
            domain=document.domain.value,
            audience=document.audience.value,
            summary=document.summary,
            content=document.content,
            safe_to_quote=hints.safe_to_quote if hints is not None else False,
            requires_domain_validation=(
                hints.requires_domain_validation if hints is not None else False
            ),
            max_context_chars=hints.max_context_chars if hints is not None else None,
        )

    def _build_blocks(self, context: PromptContext) -> list[PromptContextBlock]:
        blocks = [
            PromptContextBlock(
                kind=PromptContextBlockKind.USER_MESSAGE,
                label="User Message",
                content=context.user_context.message,
            )
        ]

        if context.conversation_context is not None and context.conversation_context.state:
            blocks.append(
                PromptContextBlock(
                    kind=PromptContextBlockKind.CONVERSATION_STATE,
                    label="Conversation State",
                    content=self._serialize_json(
                        context.conversation_context.state,
                        context.rendering_options,
                    ),
                )
            )

        if context.knowledge_context is None:
            return blocks

        for document in context.knowledge_context.documents:
            blocks.append(
                PromptContextBlock(
                    kind=PromptContextBlockKind.KNOWLEDGE_DOCUMENT,
                    label=f"Knowledge Document: {document.title}",
                    content=self._format_context_document(document, context.rendering_options),
                    metadata={
                        "document_id": document.document_id,
                        "source_path": document.source_path,
                        "domain": document.domain,
                        "audience": document.audience,
                    },
                )
            )

        return blocks

    def _format_context_document(
        self,
        document: PromptContextKnowledgeDocument,
        rendering_options: PromptContextRenderingOptions,
    ) -> str:
        summary = f"Summary: {document.summary}"

        if not document.safe_to_quote:
            return "\n".join(
                [
                    f"Document ID: {document.document_id}",
                    f"Source: {document.source_path}",
                    summary,
                    "Quoted content omitted because the document is not marked safe_to_quote.",
                ]
            )

        content = self._serialize_content(document.content, rendering_options)
        if document.max_context_chars is not None and len(content) > document.max_context_chars:
            content = content[: document.max_context_chars].rstrip()

        return "\n".join(
            [
                f"Document ID: {document.document_id}",
                f"Source: {document.source_path}",
                summary,
                "Content:",
                content,
            ]
        )

    def _compose_prompt(
        self,
        *,
        blocks: list[PromptContextBlock],
        context: PromptContext,
    ) -> tuple[str, bool]:
        sections: list[str] = []
        if context.system_instructions.instructions:
            instructions = "\n".join(
                f"- {instruction}" for instruction in context.system_instructions.instructions
            )
            sections.append(
                self._render_section(
                    label="System Instructions",
                    content=instructions,
                    rendering_options=context.rendering_options,
                )
            )

        for block in blocks:
            sections.append(
                self._render_section(
                    label=block.label,
                    content=block.content,
                    rendering_options=context.rendering_options,
                )
            )

        prompt = "\n\n".join(sections)
        if len(prompt) <= context.constraints.max_prompt_chars:
            return prompt, False

        truncation_marker = context.rendering_options.truncation_marker
        clipped_prompt = prompt[
            : context.constraints.max_prompt_chars - (len(truncation_marker) + 3)
        ].rstrip()
        return f"{clipped_prompt}\n\n{truncation_marker}", True

    def _render_section(
        self,
        *,
        label: str,
        content: str,
        rendering_options: PromptContextRenderingOptions,
    ) -> str:
        if not rendering_options.include_section_headers:
            return content
        return f"[{label}]\n{content}"

    def _serialize_content(
        self,
        content: str | dict[str, Any],
        rendering_options: PromptContextRenderingOptions,
    ) -> str:
        if isinstance(content, str):
            return content.strip()
        return self._serialize_json(content, rendering_options)

    def _serialize_json(
        self,
        value: Any,
        rendering_options: PromptContextRenderingOptions,
    ) -> str:
        separators = (",", ":") if rendering_options.json_compact else None
        return json.dumps(
            value,
            sort_keys=rendering_options.json_sort_keys,
            ensure_ascii=rendering_options.json_ensure_ascii,
            separators=separators,
        )
