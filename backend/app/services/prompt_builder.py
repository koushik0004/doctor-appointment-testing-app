from __future__ import annotations

from copy import deepcopy
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
    current_user_message: str | None = None
    previous_turns: list["PromptContextConversationTurn"] = Field(default_factory=list)
    assistant_turns: list["PromptContextConversationTurn"] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptContextConversationTurn(BaseModel):
    role: str = Field(min_length=1)
    message: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptContextWorkflowContext(BaseModel):
    active_intent: str | None = None
    workflow_status: str | None = None
    collected_fields: dict[str, Any] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    state: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptContextKnowledgeDocument(BaseModel):
    document_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    audience: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    content: str | dict[str, Any]
    include_when_intents: list[str] = Field(default_factory=list)
    exclude_when_intents: list[str] = Field(default_factory=list)
    safe_to_quote: bool = False
    requires_domain_validation: bool = False
    max_context_chars: int | None = Field(default=None, gt=0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptContextKnowledgeContext(BaseModel):
    documents: list[PromptContextKnowledgeDocument] = Field(default_factory=list)


class PromptContextKnowledgeCollection(BaseModel):
    knowledge_context: PromptContextKnowledgeContext | None = None
    included_document_ids: list[str] = Field(default_factory=list)
    excluded_document_ids: list[str] = Field(default_factory=list)
    requires_domain_validation: bool = False


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


class PromptContextValidationIssue(BaseModel):
    code: str = Field(min_length=1)
    path: str = Field(min_length=1)
    message: str = Field(min_length=1)

    model_config = ConfigDict(str_strip_whitespace=True)


class PromptContextValidationResult(BaseModel):
    is_valid: bool
    issues: list[PromptContextValidationIssue] = Field(default_factory=list)


class PromptContextConversationCollector:
    """Deterministically normalizes caller-supplied conversation state."""

    _HISTORY_KEYS = ("history", "turns", "messages")
    _TEXT_KEYS = ("text", "message", "content")
    _METADATA_SKIP_KEYS = frozenset({"history", "turns", "messages"})
    _TURN_SKIP_KEYS = frozenset({"role", "text", "message", "content"})
    _SUPPORTED_ROLES = frozenset({"user", "assistant", "system"})

    def collect(
        self,
        *,
        user_message: str,
        conversation_state: dict[str, Any],
    ) -> PromptContextConversationContext | None:
        if not conversation_state:
            return None

        raw_state = deepcopy(conversation_state)
        turns = self._normalize_turns(conversation_state)
        previous_turns = list(turns)

        if previous_turns and self._is_current_user_turn(previous_turns[-1], user_message):
            previous_turns = previous_turns[:-1]

        assistant_turns = [turn for turn in previous_turns if turn.role == "assistant"]

        return PromptContextConversationContext(
            state=raw_state,
            current_user_message=user_message,
            previous_turns=previous_turns,
            assistant_turns=assistant_turns,
            metadata=self._collect_metadata(conversation_state),
        )

    def _normalize_turns(
        self,
        conversation_state: dict[str, Any],
    ) -> list[PromptContextConversationTurn]:
        history_items = self._extract_history_items(conversation_state)
        normalized_turns: list[PromptContextConversationTurn] = []

        for item in history_items:
            if not isinstance(item, dict):
                continue

            role = str(item.get("role", "")).strip().lower()
            if role not in self._SUPPORTED_ROLES:
                continue

            message = self._extract_turn_message(item)
            if message is None:
                continue

            normalized_turns.append(
                PromptContextConversationTurn(
                    role=role,
                    message=message,
                    metadata={
                        key: deepcopy(value)
                        for key, value in item.items()
                        if key not in self._TURN_SKIP_KEYS
                    },
                )
            )

        return normalized_turns

    def _extract_history_items(self, conversation_state: dict[str, Any]) -> list[Any]:
        for key in self._HISTORY_KEYS:
            value = conversation_state.get(key)
            if isinstance(value, list):
                return value
        return []

    def _extract_turn_message(self, item: dict[str, Any]) -> str | None:
        for key in self._TEXT_KEYS:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _is_current_user_turn(
        self,
        turn: PromptContextConversationTurn,
        user_message: str,
    ) -> bool:
        return turn.role == "user" and turn.message == user_message.strip()

    def _collect_metadata(self, conversation_state: dict[str, Any]) -> dict[str, Any]:
        return {
            key: deepcopy(value)
            for key, value in conversation_state.items()
            if key not in self._METADATA_SKIP_KEYS
        }


class PromptContextWorkflowCollector:
    """Deterministically normalizes caller-supplied workflow state."""

    _WORKFLOW_CONTAINER_KEYS = ("current_workflow", "workflow_state", "workflow")
    _WORKFLOW_IDENTITY_KEYS = ("workflow_type", "workflow", "active_intent", "intent")
    _WORKFLOW_STATUS_KEYS = ("status", "workflow_status", "state")
    _COLLECTED_FIELDS_KEYS = ("draft", "collected_fields", "fields")
    _MISSING_FIELDS_KEYS = ("missing_fields", "missing")
    _WORKFLOW_SKIP_KEYS = frozenset(
        {
            "workflow_type",
            "workflow",
            "active_intent",
            "intent",
            "status",
            "workflow_status",
            "state",
            "draft",
            "collected_fields",
            "fields",
            "missing_fields",
            "missing",
        }
    )

    def collect(
        self,
        *,
        active_intent: str | None,
        conversation_state: dict[str, Any],
    ) -> PromptContextWorkflowContext | None:
        workflow_state = self._extract_workflow_state(conversation_state)
        if workflow_state is None:
            if not active_intent:
                return None
            return PromptContextWorkflowContext(active_intent=active_intent)

        raw_state = deepcopy(workflow_state)
        workflow_identity = self._extract_first_string(
            workflow_state,
            self._WORKFLOW_IDENTITY_KEYS,
        )
        workflow_status = self._extract_first_string(
            workflow_state,
            self._WORKFLOW_STATUS_KEYS,
        )
        collected_fields = self._extract_collected_fields(workflow_state)
        missing_fields = self._extract_missing_fields(workflow_state)

        return PromptContextWorkflowContext(
            active_intent=workflow_identity or active_intent,
            workflow_status=workflow_status,
            collected_fields=collected_fields,
            missing_fields=missing_fields,
            metadata=self._collect_metadata(workflow_state),
            state=raw_state,
        )

    def _extract_workflow_state(
        self,
        conversation_state: dict[str, Any],
    ) -> dict[str, Any] | None:
        context_value = conversation_state.get("context")
        if isinstance(context_value, dict):
            current_workflow = context_value.get("current_workflow")
            if isinstance(current_workflow, dict):
                return current_workflow

        for key in self._WORKFLOW_CONTAINER_KEYS:
            value = conversation_state.get(key)
            if isinstance(value, dict):
                return value

        if any(key in conversation_state for key in self._WORKFLOW_IDENTITY_KEYS):
            return conversation_state

        return None

    def _extract_first_string(
        self,
        workflow_state: dict[str, Any],
        keys: tuple[str, ...],
    ) -> str | None:
        for key in keys:
            value = workflow_state.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _extract_collected_fields(
        self,
        workflow_state: dict[str, Any],
    ) -> dict[str, Any]:
        for key in self._COLLECTED_FIELDS_KEYS:
            value = workflow_state.get(key)
            if isinstance(value, dict):
                return deepcopy(value)
        return {}

    def _extract_missing_fields(
        self,
        workflow_state: dict[str, Any],
    ) -> list[str]:
        for key in self._MISSING_FIELDS_KEYS:
            value = workflow_state.get(key)
            if isinstance(value, list):
                normalized: list[str] = []
                for item in value:
                    if isinstance(item, str) and item.strip():
                        normalized.append(item.strip())
                return normalized
        return []

    def _collect_metadata(self, workflow_state: dict[str, Any]) -> dict[str, Any]:
        return {
            key: deepcopy(value)
            for key, value in workflow_state.items()
            if key not in self._WORKFLOW_SKIP_KEYS
        }


class PromptContextKnowledgeCollector:
    """Deterministically normalizes already-selected knowledge documents."""

    def collect(
        self,
        *,
        documents: list[KnowledgeDocument],
        active_intent: str | None,
    ) -> PromptContextKnowledgeCollection:
        included_documents: list[PromptContextKnowledgeDocument] = []
        included_document_ids: list[str] = []
        excluded_document_ids: list[str] = []
        requires_domain_validation = False

        for document in documents:
            if not self._should_include_document(document, active_intent):
                excluded_document_ids.append(document.id)
                continue

            context_document = self._to_context_document(document)
            included_documents.append(context_document)
            included_document_ids.append(document.id)
            if context_document.requires_domain_validation:
                requires_domain_validation = True

        return PromptContextKnowledgeCollection(
            knowledge_context=(
                PromptContextKnowledgeContext(documents=included_documents)
                if included_documents
                else None
            ),
            included_document_ids=included_document_ids,
            excluded_document_ids=excluded_document_ids,
            requires_domain_validation=requires_domain_validation,
        )

    def _should_include_document(
        self,
        document: KnowledgeDocument,
        active_intent: str | None,
    ) -> bool:
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
            content=deepcopy(document.content),
            include_when_intents=list(hints.include_when_intents) if hints is not None else [],
            exclude_when_intents=list(hints.exclude_when_intents) if hints is not None else [],
            safe_to_quote=hints.safe_to_quote if hints is not None else False,
            requires_domain_validation=(
                hints.requires_domain_validation if hints is not None else False
            ),
            max_context_chars=hints.max_context_chars if hints is not None else None,
            metadata=deepcopy(document.metadata),
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

    def __init__(
        self,
        conversation_collector: PromptContextConversationCollector | None = None,
        workflow_collector: PromptContextWorkflowCollector | None = None,
        knowledge_collector: PromptContextKnowledgeCollector | None = None,
    ) -> None:
        self._conversation_collector = (
            conversation_collector
            if conversation_collector is not None
            else PromptContextConversationCollector()
        )
        self._workflow_collector = (
            workflow_collector
            if workflow_collector is not None
            else PromptContextWorkflowCollector()
        )
        self._knowledge_collector = (
            knowledge_collector
            if knowledge_collector is not None
            else PromptContextKnowledgeCollector()
        )

    def build(self, request: PromptBuildRequest) -> PromptBuildResult:
        context = self.build_context(request)
        validation = self.validate_context(context)
        if not validation.is_valid:
            raise ValueError(self._format_validation_error(validation.issues))
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
        workflow_context = self._workflow_collector.collect(
            active_intent=request.active_intent,
            conversation_state=request.conversation_state,
        )
        resolved_active_intent = (
            workflow_context.active_intent
            if workflow_context is not None and workflow_context.active_intent
            else request.active_intent
        )
        knowledge_collection = self._knowledge_collector.collect(
            documents=request.documents,
            active_intent=resolved_active_intent,
        )

        return PromptContext(
            metadata=PromptContextMetadata(
                active_intent=resolved_active_intent,
                included_document_ids=knowledge_collection.included_document_ids,
                excluded_document_ids=knowledge_collection.excluded_document_ids,
                requires_domain_validation=knowledge_collection.requires_domain_validation,
            ),
            user_context=PromptContextUserContext(message=request.user_message),
            conversation_context=self._conversation_collector.collect(
                user_message=request.user_message,
                conversation_state=request.conversation_state,
            ),
            workflow_context=workflow_context,
            knowledge_context=knowledge_collection.knowledge_context,
            system_instructions=PromptContextSystemInstructions(
                instructions=list(request.system_instructions)
            ),
            constraints=PromptContextConstraints(max_prompt_chars=request.max_prompt_chars),
        )

    def validate_context(self, context: PromptContext) -> PromptContextValidationResult:
        issues: list[PromptContextValidationIssue] = []

        if not isinstance(context.metadata, PromptContextMetadata):
            issues.append(
                PromptContextValidationIssue(
                    code="invalid_section",
                    path="metadata",
                    message="metadata must be a PromptContextMetadata instance.",
                )
            )

        if not isinstance(context.user_context, PromptContextUserContext):
            issues.append(
                PromptContextValidationIssue(
                    code="invalid_section",
                    path="user_context",
                    message="user_context must be a PromptContextUserContext instance.",
                )
            )
        elif not context.user_context.message.strip():
            issues.append(
                PromptContextValidationIssue(
                    code="empty_user_message",
                    path="user_context.message",
                    message="user_context.message must be non-empty.",
                )
            )

        if context.conversation_context is not None and not isinstance(
            context.conversation_context, PromptContextConversationContext
        ):
            issues.append(
                PromptContextValidationIssue(
                    code="invalid_section",
                    path="conversation_context",
                    message=(
                        "conversation_context must be a PromptContextConversationContext "
                        "instance when provided."
                    ),
                )
            )
        elif context.conversation_context is not None:
            for index, turn in enumerate(context.conversation_context.previous_turns):
                if not isinstance(turn, PromptContextConversationTurn):
                    issues.append(
                        PromptContextValidationIssue(
                            code="invalid_section",
                            path=f"conversation_context.previous_turns[{index}]",
                            message=(
                                "conversation_context.previous_turns must contain "
                                "PromptContextConversationTurn instances."
                            ),
                        )
                    )
            for index, turn in enumerate(context.conversation_context.assistant_turns):
                if not isinstance(turn, PromptContextConversationTurn):
                    issues.append(
                        PromptContextValidationIssue(
                            code="invalid_section",
                            path=f"conversation_context.assistant_turns[{index}]",
                            message=(
                                "conversation_context.assistant_turns must contain "
                                "PromptContextConversationTurn instances."
                            ),
                        )
                    )
                elif turn.role != "assistant":
                    issues.append(
                        PromptContextValidationIssue(
                            code="invalid_conversation_metadata",
                            path=f"conversation_context.assistant_turns[{index}].role",
                            message=(
                                "conversation_context.assistant_turns may only contain "
                                "assistant turns."
                            ),
                        )
                    )

        if context.workflow_context is not None and not isinstance(
            context.workflow_context, PromptContextWorkflowContext
        ):
            issues.append(
                PromptContextValidationIssue(
                    code="invalid_section",
                    path="workflow_context",
                    message=(
                        "workflow_context must be a PromptContextWorkflowContext instance "
                        "when provided."
                    ),
                )
        )

        if not isinstance(context.system_instructions, PromptContextSystemInstructions):
            issues.append(
                PromptContextValidationIssue(
                    code="invalid_section",
                    path="system_instructions",
                    message=(
                        "system_instructions must be a PromptContextSystemInstructions "
                        "instance."
                    ),
                )
            )

        if not isinstance(context.constraints, PromptContextConstraints):
            issues.append(
                PromptContextValidationIssue(
                    code="invalid_section",
                    path="constraints",
                    message="constraints must be a PromptContextConstraints instance.",
                )
            )
        else:
            if isinstance(context.rendering_options, PromptContextRenderingOptions):
                min_prompt_chars = len(context.rendering_options.truncation_marker) + 3
                if context.constraints.max_prompt_chars < min_prompt_chars:
                    issues.append(
                        PromptContextValidationIssue(
                            code="invalid_constraint",
                            path="constraints.max_prompt_chars",
                            message=(
                                "constraints.max_prompt_chars must allow space for the "
                                "truncation marker."
                            ),
                        )
                    )

        if not isinstance(context.rendering_options, PromptContextRenderingOptions):
            issues.append(
                PromptContextValidationIssue(
                    code="invalid_section",
                    path="rendering_options",
                    message=(
                        "rendering_options must be a PromptContextRenderingOptions instance."
                    ),
                )
            )
        else:
            if "\n" in context.rendering_options.truncation_marker:
                issues.append(
                    PromptContextValidationIssue(
                        code="invalid_rendering_option",
                        path="rendering_options.truncation_marker",
                        message="rendering_options.truncation_marker must be single-line.",
                    )
                )

        if context.knowledge_context is not None and not isinstance(
            context.knowledge_context, PromptContextKnowledgeContext
        ):
            issues.append(
                PromptContextValidationIssue(
                    code="invalid_section",
                    path="knowledge_context",
                    message=(
                        "knowledge_context must be a PromptContextKnowledgeContext instance "
                        "when provided."
                    ),
                )
            )

        included_ids = (
            list(context.metadata.included_document_ids)
            if isinstance(context.metadata, PromptContextMetadata)
            else []
        )
        excluded_ids = (
            list(context.metadata.excluded_document_ids)
            if isinstance(context.metadata, PromptContextMetadata)
            else []
        )
        included_id_set = set(included_ids)
        excluded_id_set = set(excluded_ids)
        overlap = sorted(included_id_set & excluded_id_set)
        if overlap:
            issues.append(
                PromptContextValidationIssue(
                    code="inconsistent_document_metadata",
                    path="metadata.included_document_ids",
                    message=(
                        "included_document_ids and excluded_document_ids must be disjoint."
                    ),
                )
            )

        knowledge_document_ids: list[str] = []
        if isinstance(context.knowledge_context, PromptContextKnowledgeContext):
            for index, document in enumerate(context.knowledge_context.documents):
                if not isinstance(document, PromptContextKnowledgeDocument):
                    issues.append(
                        PromptContextValidationIssue(
                            code="invalid_section",
                            path=f"knowledge_context.documents[{index}]",
                            message=(
                                "knowledge documents must be PromptContextKnowledgeDocument "
                                "instances."
                            ),
                        )
                    )
                    continue
                knowledge_document_ids.append(document.document_id)

        duplicate_document_ids = sorted(
            {
                document_id
                for document_id in knowledge_document_ids
                if knowledge_document_ids.count(document_id) > 1
            }
        )
        if duplicate_document_ids:
            issues.append(
                PromptContextValidationIssue(
                    code="duplicate_document_ids",
                    path="knowledge_context.documents",
                    message=(
                        "knowledge_context.documents must not contain duplicate "
                        "document_id values."
                    ),
                )
            )

        if knowledge_document_ids != included_ids:
            issues.append(
                PromptContextValidationIssue(
                    code="inconsistent_document_metadata",
                    path="metadata.included_document_ids",
                    message=(
                        "metadata.included_document_ids must match knowledge_context "
                        "document order exactly."
                    ),
                )
            )

        included_docs_in_excluded = sorted(set(knowledge_document_ids) & excluded_id_set)
        if included_docs_in_excluded:
            issues.append(
                PromptContextValidationIssue(
                    code="inconsistent_document_metadata",
                    path="metadata.excluded_document_ids",
                    message=(
                        "excluded_document_ids must not reference included knowledge "
                        "documents."
                    ),
                )
            )

        if isinstance(context.workflow_context, PromptContextWorkflowContext):
            workflow_intent = context.workflow_context.active_intent
            metadata_intent = (
                context.metadata.active_intent
                if isinstance(context.metadata, PromptContextMetadata)
                else None
            )
            for index, field_name in enumerate(context.workflow_context.missing_fields):
                if not isinstance(field_name, str) or not field_name.strip():
                    issues.append(
                        PromptContextValidationIssue(
                            code="invalid_workflow_metadata",
                            path=f"workflow_context.missing_fields[{index}]",
                            message=(
                                "workflow_context.missing_fields must contain non-empty "
                                "string values."
                            ),
                        )
                    )
            if workflow_intent and workflow_intent != metadata_intent:
                issues.append(
                    PromptContextValidationIssue(
                        code="inconsistent_workflow_metadata",
                        path="workflow_context.active_intent",
                        message=(
                            "workflow_context.active_intent must match metadata.active_intent."
                        ),
                    )
                )
            if not workflow_intent:
                issues.append(
                    PromptContextValidationIssue(
                        code="inconsistent_workflow_metadata",
                        path="workflow_context.active_intent",
                        message=(
                            "workflow_context.active_intent must be non-empty when "
                            "workflow_context is provided."
                        ),
                    )
                )

        return PromptContextValidationResult(
            is_valid=not issues,
            issues=issues,
        )

    def _build_blocks(self, context: PromptContext) -> list[PromptContextBlock]:
        blocks = [
            PromptContextBlock(
                kind=PromptContextBlockKind.USER_MESSAGE,
                label="User Message",
                content=context.user_context.message,
            )
        ]

        if context.conversation_context is not None and self._has_conversation_context_content(
            context.conversation_context
        ):
            blocks.append(
                PromptContextBlock(
                    kind=PromptContextBlockKind.CONVERSATION_STATE,
                    label="Conversation State",
                    content=self._serialize_json(
                        self._serialize_conversation_context(context.conversation_context),
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

    def _has_conversation_context_content(
        self,
        conversation_context: PromptContextConversationContext,
    ) -> bool:
        return bool(
            conversation_context.state
            or conversation_context.current_user_message
            or conversation_context.previous_turns
            or conversation_context.assistant_turns
            or conversation_context.metadata
        )

    def _serialize_conversation_context(
        self,
        conversation_context: PromptContextConversationContext,
    ) -> dict[str, Any]:
        if (
            not conversation_context.previous_turns
            and not conversation_context.assistant_turns
            and not conversation_context.metadata
            and conversation_context.current_user_message is None
        ):
            return deepcopy(conversation_context.state)

        serialized: dict[str, Any] = {
            "current_user_message": conversation_context.current_user_message,
            "previous_turns": [
                self._serialize_conversation_turn(turn)
                for turn in conversation_context.previous_turns
            ],
            "assistant_turns": [
                self._serialize_conversation_turn(turn)
                for turn in conversation_context.assistant_turns
            ],
            "metadata": deepcopy(conversation_context.metadata),
            "state": deepcopy(conversation_context.state),
        }
        return serialized

    def _serialize_conversation_turn(
        self,
        turn: PromptContextConversationTurn,
    ) -> dict[str, Any]:
        return {
            "role": turn.role,
            "message": turn.message,
            "metadata": deepcopy(turn.metadata),
        }

    def _format_validation_error(
        self,
        issues: list[PromptContextValidationIssue],
    ) -> str:
        serialized_issues = [
            {
                "code": issue.code,
                "path": issue.path,
                "message": issue.message,
            }
            for issue in issues
        ]
        return f"PromptContext validation failed: {json.dumps(serialized_issues, sort_keys=True)}"
