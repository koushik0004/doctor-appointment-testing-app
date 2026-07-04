from app.knowledge import (
    KnowledgeDocument,
    KnowledgeDocumentAudience,
    KnowledgeDocumentDomain,
    KnowledgeDocumentSourceType,
    KnowledgeDocumentStatus,
    KnowledgePromptHints,
)
from app.services.prompt_builder import (
    PromptBuildRequest,
    PromptBuilderService,
    PromptContext,
    PromptContextConstraints,
    PromptContextKnowledgeContext,
    PromptContextKnowledgeDocument,
    PromptContextMetadata,
    PromptContextRenderingOptions,
    PromptContextSystemInstructions,
    PromptContextUserContext,
    PromptContextValidationResult,
    PromptContextWorkflowContext,
)


def _build_document(
    *,
    document_id: str,
    title: str = "Test Document",
    summary: str = "Test summary.",
    content: str | dict = "Test content.",
    include_when_intents: list[str] | None = None,
    exclude_when_intents: list[str] | None = None,
    safe_to_quote: bool = True,
    requires_domain_validation: bool = False,
    max_context_chars: int | None = None,
) -> KnowledgeDocument:
    return KnowledgeDocument(
        id=document_id,
        title=title,
        source_type=KnowledgeDocumentSourceType.MARKDOWN,
        source_path=f"faq/{document_id}.md",
        domain=KnowledgeDocumentDomain.FAQ,
        audience=KnowledgeDocumentAudience.PATIENT,
        status=KnowledgeDocumentStatus.ACTIVE,
        version="1.0",
        summary=summary,
        content=content,
        prompt_hints=KnowledgePromptHints(
            include_when_intents=include_when_intents or [],
            exclude_when_intents=exclude_when_intents or [],
            safe_to_quote=safe_to_quote,
            requires_domain_validation=requires_domain_validation,
            max_context_chars=max_context_chars,
        ),
    )


def test_prompt_builder_builds_deterministic_prompt_with_context_blocks():
    service = PromptBuilderService()
    document = _build_document(
        document_id="faq.booking",
        title="Booking Help",
        content={"steps": ["choose doctor", "pick time"]},
    )

    result = service.build(
        PromptBuildRequest(
            user_message="Help me book an appointment",
            conversation_state={"workflow": "BOOK_APPOINTMENT", "missing": ["date"]},
            documents=[document],
            system_instructions=["Use only provided context.", "Do not invent appointment data."],
        )
    )

    assert result.truncated is False
    assert result.included_document_ids == ["faq.booking"]
    assert result.excluded_document_ids == []
    assert result.blocks[0].label == "User Message"
    assert result.blocks[1].label == "Conversation State"
    assert result.blocks[2].metadata["document_id"] == "faq.booking"
    assert "[System Instructions]" in result.prompt
    assert '"missing":["date"]' in result.prompt
    assert '"steps":["choose doctor","pick time"]' in result.prompt


def test_prompt_builder_creates_canonical_prompt_context_with_optional_sections():
    service = PromptBuilderService()
    document = _build_document(
        document_id="faq.booking",
        title="Booking Help",
        include_when_intents=["BOOK_APPOINTMENT"],
        requires_domain_validation=True,
    )

    context = service.build_context(
        PromptBuildRequest(
            user_message="Help me book",
            conversation_state={"draft": {"doctor_id": 1}},
            documents=[document],
            active_intent="BOOK_APPOINTMENT",
            system_instructions=["Use only provided context."],
            max_prompt_chars=2500,
        )
    )

    assert context.metadata.active_intent == "BOOK_APPOINTMENT"
    assert context.metadata.included_document_ids == ["faq.booking"]
    assert context.metadata.excluded_document_ids == []
    assert context.metadata.requires_domain_validation is True
    assert context.user_context.message == "Help me book"
    assert context.conversation_context is not None
    assert context.conversation_context.state == {"draft": {"doctor_id": 1}}
    assert context.workflow_context is not None
    assert context.workflow_context.active_intent == "BOOK_APPOINTMENT"
    assert context.knowledge_context is not None
    assert context.knowledge_context.documents[0].document_id == "faq.booking"
    assert context.system_instructions.instructions == ["Use only provided context."]
    assert context.constraints.max_prompt_chars == 2500


def test_prompt_builder_context_uses_deterministic_defaults_for_optional_sections():
    service = PromptBuilderService()

    context = service.build_context(
        PromptBuildRequest(
            user_message="Hello there",
        )
    )

    assert context.metadata.included_document_ids == []
    assert context.metadata.excluded_document_ids == []
    assert context.metadata.requires_domain_validation is False
    assert context.conversation_context is None
    assert context.workflow_context is None
    assert context.knowledge_context is None
    assert context.system_instructions.instructions == []
    assert context.constraints == PromptContextConstraints()
    assert context.rendering_options == PromptContextRenderingOptions()


def test_prompt_builder_validates_a_valid_prompt_context():
    service = PromptBuilderService()
    context = service.build_context(
        PromptBuildRequest(
            user_message="Help me book",
            documents=[_build_document(document_id="faq.booking")],
        )
    )

    validation = service.validate_context(context)

    assert validation == PromptContextValidationResult(is_valid=True, issues=[])


def test_prompt_builder_validation_rejects_duplicate_knowledge_document_ids():
    service = PromptBuilderService()
    duplicate_document = PromptContextKnowledgeDocument(
        document_id="faq.booking",
        title="Booking Help",
        source_path="faq/booking.md",
        domain="faq",
        audience="patient",
        summary="Booking help summary.",
        content="Booking help content.",
        safe_to_quote=True,
    )
    context = PromptContext(
        metadata=PromptContextMetadata(
            included_document_ids=["faq.booking", "faq.booking"],
        ),
        user_context=PromptContextUserContext(message="Help me book"),
        knowledge_context=PromptContextKnowledgeContext(
            documents=[duplicate_document, duplicate_document]
        ),
    )

    validation = service.validate_context(context)

    assert validation.is_valid is False
    assert any(issue.code == "duplicate_document_ids" for issue in validation.issues)


def test_prompt_builder_validation_rejects_invalid_constraints():
    service = PromptBuilderService()
    context = PromptContext.model_construct(
        metadata=PromptContextMetadata(),
        user_context=PromptContextUserContext(message="Need help"),
        system_instructions=PromptContextSystemInstructions(),
        constraints=PromptContextConstraints.model_construct(max_prompt_chars=5),
        rendering_options=PromptContextRenderingOptions(),
    )

    validation = service.validate_context(context)

    assert validation.is_valid is False
    assert any(issue.code == "invalid_constraint" for issue in validation.issues)


def test_prompt_builder_validation_rejects_invalid_rendering_options():
    service = PromptBuilderService()
    context = PromptContext.model_construct(
        metadata=PromptContextMetadata(),
        user_context=PromptContextUserContext(message="Need help"),
        system_instructions=PromptContextSystemInstructions(),
        constraints=PromptContextConstraints(),
        rendering_options=PromptContextRenderingOptions.model_construct(
            include_section_headers=True,
            json_sort_keys=True,
            json_ensure_ascii=True,
            json_compact=True,
            truncation_marker="[TRUNCATED]\nMORE",
        ),
    )

    validation = service.validate_context(context)

    assert validation.is_valid is False
    assert any(issue.code == "invalid_rendering_option" for issue in validation.issues)


def test_prompt_builder_validation_rejects_inconsistent_workflow_metadata():
    service = PromptBuilderService()
    context = PromptContext(
        metadata=PromptContextMetadata(active_intent="BOOK_APPOINTMENT"),
        user_context=PromptContextUserContext(message="Need help"),
        workflow_context=PromptContextWorkflowContext(active_intent="CANCEL_APPOINTMENT"),
    )

    validation = service.validate_context(context)

    assert validation.is_valid is False
    assert any(issue.code == "inconsistent_workflow_metadata" for issue in validation.issues)


def test_prompt_builder_applies_prompt_hints_as_constraints():
    service = PromptBuilderService()
    included_document = _build_document(
        document_id="faq.allowed",
        include_when_intents=["BOOK_APPOINTMENT"],
        requires_domain_validation=True,
        safe_to_quote=False,
    )
    excluded_document = _build_document(
        document_id="faq.excluded",
        exclude_when_intents=["BOOK_APPOINTMENT"],
    )

    result = service.build(
        PromptBuildRequest(
            user_message="Can I book for tomorrow?",
            active_intent="BOOK_APPOINTMENT",
            documents=[included_document, excluded_document],
        )
    )

    assert result.included_document_ids == ["faq.allowed"]
    assert result.excluded_document_ids == ["faq.excluded"]
    assert result.requires_domain_validation is True
    assert "Quoted content omitted because the document is not marked safe_to_quote." in result.prompt
    assert "faq.excluded" not in result.prompt


def test_prompt_builder_raises_deterministic_validation_error_before_rendering():
    class InvalidContextPromptBuilderService(PromptBuilderService):
        def build_context(self, request: PromptBuildRequest) -> PromptContext:
            return PromptContext.model_construct(
                metadata=PromptContextMetadata(),
                user_context=PromptContextUserContext.model_construct(message=" "),
                system_instructions=PromptContextSystemInstructions(),
                constraints=PromptContextConstraints(),
                rendering_options=PromptContextRenderingOptions(),
            )

    service = InvalidContextPromptBuilderService()

    try:
        service.build(PromptBuildRequest(user_message="Ignored by override"))
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected validation error")

    assert message.startswith("PromptContext validation failed:")
    assert '"code": "empty_user_message"' in message


def test_prompt_builder_enforces_document_and_total_prompt_budgets():
    service = PromptBuilderService()
    document = _build_document(
        document_id="faq.long",
        summary="Long document summary.",
        content="A" * 200,
        max_context_chars=40,
    )

    clipped_result = service.build(
        PromptBuildRequest(
            user_message="Summarize the policy",
            documents=[document],
            max_prompt_chars=400,
        )
    )
    truncated_result = service.build(
        PromptBuildRequest(
            user_message="Summarize the policy",
            documents=[document],
            max_prompt_chars=180,
        )
    )

    assert clipped_result.truncated is False
    assert "A" * 60 not in clipped_result.prompt
    assert "A" * 40 in clipped_result.prompt
    assert truncated_result.truncated is True
    assert "[TRUNCATED]" in truncated_result.prompt
