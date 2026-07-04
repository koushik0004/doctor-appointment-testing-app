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
        blocks = [
            PromptContextBlock(
                kind=PromptContextBlockKind.USER_MESSAGE,
                label="User Message",
                content=request.user_message,
            )
        ]
        included_document_ids: list[str] = []
        excluded_document_ids: list[str] = []
        requires_domain_validation = False

        if request.conversation_state:
            blocks.append(
                PromptContextBlock(
                    kind=PromptContextBlockKind.CONVERSATION_STATE,
                    label="Conversation State",
                    content=self._serialize_json(request.conversation_state),
                )
            )

        for document in request.documents:
            if not self._should_include_document(document, request.active_intent):
                excluded_document_ids.append(document.id)
                continue

            block_content = self._format_document_content(document)
            if not block_content:
                excluded_document_ids.append(document.id)
                continue

            hints = document.prompt_hints
            if hints is not None and hints.requires_domain_validation:
                requires_domain_validation = True

            blocks.append(
                PromptContextBlock(
                    kind=PromptContextBlockKind.KNOWLEDGE_DOCUMENT,
                    label=f"Knowledge Document: {document.title}",
                    content=block_content,
                    metadata={
                        "document_id": document.id,
                        "source_path": document.source_path,
                        "domain": document.domain.value,
                        "audience": document.audience.value,
                    },
                )
            )
            included_document_ids.append(document.id)

        prompt, truncated = self._compose_prompt(
            blocks=blocks,
            system_instructions=request.system_instructions,
            max_prompt_chars=request.max_prompt_chars,
        )

        return PromptBuildResult(
            prompt=prompt,
            blocks=blocks,
            included_document_ids=included_document_ids,
            excluded_document_ids=excluded_document_ids,
            truncated=truncated,
            requires_domain_validation=requires_domain_validation,
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

    def _format_document_content(self, document: KnowledgeDocument) -> str:
        hints = document.prompt_hints
        summary = f"Summary: {document.summary}"
        content_limit = hints.max_context_chars if hints is not None else None

        if hints is not None and not hints.safe_to_quote:
            return "\n".join(
                [
                    f"Document ID: {document.id}",
                    f"Source: {document.source_path}",
                    summary,
                    "Quoted content omitted because the document is not marked safe_to_quote.",
                ]
            )

        content = self._serialize_content(document.content)
        if content_limit is not None and len(content) > content_limit:
            content = content[:content_limit].rstrip()

        return "\n".join(
            [
                f"Document ID: {document.id}",
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
        system_instructions: list[str],
        max_prompt_chars: int,
    ) -> tuple[str, bool]:
        sections: list[str] = []
        if system_instructions:
            instructions = "\n".join(f"- {instruction}" for instruction in system_instructions)
            sections.append(f"[System Instructions]\n{instructions}")

        for block in blocks:
            sections.append(f"[{block.label}]\n{block.content}")

        prompt = "\n\n".join(sections)
        if len(prompt) <= max_prompt_chars:
            return prompt, False

        clipped_prompt = prompt[: max_prompt_chars - 14].rstrip()
        return f"{clipped_prompt}\n\n[TRUNCATED]", True

    def _serialize_content(self, content: str | dict[str, Any]) -> str:
        if isinstance(content, str):
            return content.strip()
        return self._serialize_json(content)

    def _serialize_json(self, value: Any) -> str:
        return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
