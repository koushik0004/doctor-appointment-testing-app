from pathlib import Path

import pytest

from app.knowledge import (
    FileSystemKnowledgeLoader,
    InMemoryKnowledgeRepository,
    KnowledgeDocumentDomain,
    KnowledgeDocumentSourceType,
    KnowledgeValidationError,
)


def _write_valid_markdown(path: Path, *, document_id: str = "faq.test") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
id: {document_id}
title: Test FAQ
domain: faq
audience: patient
status: active
version: "1.0"
tags:
  - test
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
  "domain": "capability",
  "audience": "assistant",
  "status": "active",
  "version": "1.0",
  "tags": ["test", "capability"],
  "priority": 20,
  "summary": "Test capability summary.",
  "content": {
    "can_help_with": ["tests"]
  }
}
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
    assert markdown.prompt_hints is not None
    assert markdown.prompt_hints.safe_to_quote is True
    assert documents[1].source_type == KnowledgeDocumentSourceType.JSON
    assert documents[1].content == {"can_help_with": ["tests"]}


def test_loader_loads_bundled_sources():
    sources_root = Path(__file__).resolve().parents[1] / "app" / "knowledge" / "sources"

    documents = FileSystemKnowledgeLoader(sources_root).load()

    assert {document.id for document in documents} == {
        "capabilities.assistant.v1",
        "faq.booking.general",
        "faq.cancellation.general",
    }


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
