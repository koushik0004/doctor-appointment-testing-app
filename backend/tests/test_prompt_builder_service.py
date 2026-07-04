from app.knowledge import (
    KnowledgeDocument,
    KnowledgeDocumentAudience,
    KnowledgeDocumentDomain,
    KnowledgeDocumentSourceType,
    KnowledgeDocumentStatus,
    KnowledgePromptHints,
)
from app.services.prompt_builder import PromptBuildRequest, PromptBuilderService


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
