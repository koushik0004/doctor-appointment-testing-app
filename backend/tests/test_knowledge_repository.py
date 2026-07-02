from pathlib import Path

import pytest

from app.knowledge import (
    FileSystemKnowledgeLoader,
    InMemoryKnowledgeRepository,
    KnowledgeDocumentDomain,
    KnowledgeDocumentSourceType,
    KnowledgeRetrievalService,
    KnowledgeValidationError,
)


def _write_valid_markdown(path: Path, *, document_id: str = "faq.test") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
id: {document_id}
title: Test FAQ
category: general
domain: faq
audience: patient
status: active
version: "1.0"
tags:
  - test
keywords:
  - test faq
synonyms:
  - sample faq
aliases:
  - help test
priority: 10
summary: Test FAQ summary.
prompt_hints:
  include_when_intents:
    - APPOINTMENT_HELP
  exclude_when_intents: []
  safe_to_quote: true
  requires_domain_validation: false
  max_context_chars: 500
---

# Test FAQ

This is test knowledge.
""",
        encoding="utf-8",
    )


def _write_valid_json(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """{
  "id": "capabilities.test",
  "title": "Test Capabilities",
  "category": "assistant",
  "domain": "capability",
  "audience": "assistant",
  "status": "active",
  "version": "1.0",
  "tags": ["test", "capability"],
  "keywords": ["assistant capabilities"],
  "synonyms": ["assistant help"],
  "aliases": ["what can you do"],
  "priority": 20,
  "summary": "Test capability summary.",
  "content": {
    "can_help_with": ["tests"]
  }
}
""",
        encoding="utf-8",
    )


def _write_markdown(
    path: Path,
    *,
    document_id: str,
    title: str,
    summary: str,
    content: str,
    tags: list[str] | None = None,
    keywords: list[str] | None = None,
    synonyms: list[str] | None = None,
    aliases: list[str] | None = None,
    category: str = "general",
    priority: int = 10,
    status: str = "active",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tag_lines = "\n".join(f"  - {tag}" for tag in tags or [])
    keyword_lines = "\n".join(f"  - {keyword}" for keyword in keywords or [])
    synonym_lines = "\n".join(f"  - {synonym}" for synonym in synonyms or [])
    alias_lines = "\n".join(f"  - {alias}" for alias in aliases or [])
    path.write_text(
        f"""---
id: {document_id}
title: {title}
category: {category}
domain: faq
audience: patient
status: {status}
version: "1.0"
tags:
{tag_lines}
keywords:
{keyword_lines}
synonyms:
{synonym_lines}
aliases:
{alias_lines}
priority: {priority}
summary: {summary}
---

{content}
""",
        encoding="utf-8",
    )


def test_loader_loads_markdown_and_json_documents(tmp_path):
    _write_valid_markdown(tmp_path / "faq" / "booking.md")
    _write_valid_json(tmp_path / "structured" / "capabilities.json")

    documents = FileSystemKnowledgeLoader(tmp_path).load()

    assert [document.id for document in documents] == ["faq.test", "capabilities.test"]
    markdown = documents[0]
    assert markdown.source_type == KnowledgeDocumentSourceType.MARKDOWN
    assert markdown.source_path == "faq/booking.md"
    assert markdown.content.startswith("# Test FAQ")
    assert markdown.category == "general"
    assert markdown.keywords == ["test faq"]
    assert markdown.synonyms == ["sample faq"]
    assert markdown.aliases == ["help test"]
    assert markdown.prompt_hints is not None
    assert markdown.prompt_hints.safe_to_quote is True
    assert documents[1].source_type == KnowledgeDocumentSourceType.JSON
    assert documents[1].category == "assistant"
    assert documents[1].content == {"can_help_with": ["tests"]}


def test_loader_loads_bundled_sources():
    sources_root = Path(__file__).resolve().parents[1] / "app" / "knowledge" / "sources"

    documents = FileSystemKnowledgeLoader(sources_root).load()

    assert {document.id for document in documents} == {
        "faq.consultation.hours",
        "faq.preparation.general",
        "capabilities.assistant.v1",
        "faq.booking.general",
        "faq.cancellation.general",
        "faq.insurance.general",
        "faq.parking.general",
        "faq.payment.methods",
        "faq.telemedicine.general",
    }


def test_retrieval_service_matches_bundled_faq_documents():
    sources_root = Path(__file__).resolve().parents[1] / "app" / "knowledge" / "sources"
    repository = InMemoryKnowledgeRepository(FileSystemKnowledgeLoader(sources_root))
    service = KnowledgeRetrievalService(repository)

    consultation_match = service.retrieve_top_match("What are your consultation hours?")
    telemedicine_match = service.retrieve_top_match("What is telemedicine?")
    online_consultation_match = service.retrieve_top_match("Do you provide online consultation?")
    payment_match = service.retrieve_top_match("What payment methods are accepted?")
    preparation_match = service.retrieve_top_match("How do I prepare before my appointment?")

    assert consultation_match is not None
    assert consultation_match.document.id == "faq.consultation.hours"
    assert "hour" in consultation_match.matched_terms

    assert telemedicine_match is not None
    assert telemedicine_match.document.id == "faq.telemedicine.general"
    assert "telemedicine" in telemedicine_match.matched_terms

    assert online_consultation_match is not None
    assert online_consultation_match.document.id == "faq.telemedicine.general"
    assert "online" in online_consultation_match.matched_terms

    assert payment_match is not None
    assert payment_match.document.id == "faq.payment.methods"
    assert "payment" in payment_match.matched_terms

    assert preparation_match is not None
    assert preparation_match.document.id == "faq.preparation.general"
    assert "prepare" in preparation_match.matched_terms


def test_repository_caches_documents_until_forced_reload(tmp_path):
    source = tmp_path / "faq" / "booking.md"
    _write_valid_markdown(source, document_id="faq.cached")

    repository = InMemoryKnowledgeRepository(FileSystemKnowledgeLoader(tmp_path))

    assert repository.load()[0].title == "Test FAQ"
    source.write_text(source.read_text(encoding="utf-8").replace("Test FAQ", "Updated FAQ"), encoding="utf-8")

    assert repository.load()[0].title == "Test FAQ"
    assert repository.load(force_reload=True)[0].title == "Updated FAQ"


def test_repository_supports_exact_metadata_filters_only(tmp_path):
    _write_valid_markdown(tmp_path / "faq" / "booking.md", document_id="faq.booking")
    _write_valid_json(tmp_path / "structured" / "capabilities.json")

    repository = InMemoryKnowledgeRepository(FileSystemKnowledgeLoader(tmp_path))

    assert repository.get("faq.booking") is not None
    assert [document.id for document in repository.by_domain(KnowledgeDocumentDomain.FAQ)] == ["faq.booking"]
    assert [document.id for document in repository.by_tag("capability")] == ["capabilities.test"]


def test_loader_rejects_duplicate_document_ids(tmp_path):
    _write_valid_markdown(tmp_path / "faq" / "booking.md", document_id="faq.duplicate")
    _write_valid_markdown(tmp_path / "faq" / "fees.md", document_id="faq.duplicate")

    with pytest.raises(KnowledgeValidationError, match="Duplicate knowledge document id"):
        FileSystemKnowledgeLoader(tmp_path).load()


def test_loader_rejects_invalid_document_schema(tmp_path):
    source = tmp_path / "faq" / "invalid.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        """---
id: faq.invalid
title: Invalid FAQ
domain: faq
audience: patient
status: active
version: "1.0"
---

Missing required summary.
""",
        encoding="utf-8",
    )

    with pytest.raises(KnowledgeValidationError, match="Invalid knowledge document"):
        FileSystemKnowledgeLoader(tmp_path).load()


def test_retrieval_service_returns_top_title_match(tmp_path):
    _write_markdown(
        tmp_path / "faq" / "booking.md",
        document_id="faq.booking",
        title="Booking Appointments",
        summary="General visit scheduling help.",
        content="Patients can choose a doctor and available time.",
        tags=["appointments"],
        keywords=["book appointment"],
        priority=1,
    )
    _write_markdown(
        tmp_path / "faq" / "fees.md",
        document_id="faq.fees",
        title="Payment Questions",
        summary="Booking fees and appointment payments.",
        content="Patients can ask about appointment fees.",
        tags=["booking"],
        keywords=["payment questions"],
        priority=50,
    )

    repository = InMemoryKnowledgeRepository(FileSystemKnowledgeLoader(tmp_path))
    service = KnowledgeRetrievalService(repository)

    assert service.retrieve_top("How do I book an appointment?").id == "faq.booking"


def test_retrieval_service_supports_content_keyword_matching(tmp_path):
    _write_markdown(
        tmp_path / "faq" / "cancellation.md",
        document_id="faq.cancellation",
        title="Appointment Changes",
        summary="Cancel or reschedule an existing visit.",
        content="Use your confirmation details before requesting cancellation.",
        tags=["support"],
    )

    repository = InMemoryKnowledgeRepository(FileSystemKnowledgeLoader(tmp_path))
    service = KnowledgeRetrievalService(repository)

    match = service.retrieve_top_match("I need cancellation help")

    assert match is not None
    assert match.document.id == "faq.cancellation"
    assert "cancellation" in match.matched_terms


def test_retrieval_service_prioritizes_keyword_and_alias_matches_over_body_only_hits(tmp_path):
    _write_markdown(
        tmp_path / "faq" / "booking.md",
        document_id="faq.booking",
        title="Booking Appointment Help",
        summary="Patients can provide contact details during booking.",
        content="Provide your details to complete the appointment request.",
        tags=["booking"],
    )
    _write_markdown(
        tmp_path / "faq" / "telemedicine.md",
        document_id="faq.telemedicine",
        title="Telemedicine Appointments",
        summary="Remote visits supported by video.",
        content="Telemedicine is an online doctor consultation.",
        tags=["telemedicine"],
        keywords=["online consultation"],
        synonyms=["virtual appointment"],
        aliases=["do you provide online consultation"],
        category="telemedicine",
    )

    repository = InMemoryKnowledgeRepository(FileSystemKnowledgeLoader(tmp_path))
    service = KnowledgeRetrievalService(repository)

    match = service.retrieve_top_match("Do you provide online consultation?")

    assert match is not None
    assert match.document.id == "faq.telemedicine"
    assert "online" in match.matched_terms


def test_retrieval_service_returns_none_for_no_match(tmp_path):
    _write_valid_markdown(tmp_path / "faq" / "booking.md")

    repository = InMemoryKnowledgeRepository(FileSystemKnowledgeLoader(tmp_path))
    service = KnowledgeRetrievalService(repository)

    assert service.retrieve_top("unrelated pharmacy refill") is None


def test_retrieval_service_uses_active_repository_documents_only(tmp_path):
    _write_markdown(
        tmp_path / "faq" / "deprecated.md",
        document_id="faq.old",
        title="Legacy Cancellation Help",
        summary="Old cancellation instructions.",
        content="Deprecated cancellation instructions.",
        status="deprecated",
    )
    _write_markdown(
        tmp_path / "faq" / "active.md",
        document_id="faq.active",
        title="Active Visit Help",
        summary="Current visit support instructions.",
        content="Active cancellation support guidance.",
    )

    repository = InMemoryKnowledgeRepository(FileSystemKnowledgeLoader(tmp_path))
    service = KnowledgeRetrievalService(repository)

    assert service.retrieve_top("cancellation").id == "faq.active"
