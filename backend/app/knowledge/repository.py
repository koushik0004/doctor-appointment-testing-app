from __future__ import annotations

from app.knowledge.documents import KnowledgeDocument, KnowledgeDocumentDomain, KnowledgeDocumentStatus
from app.knowledge.loader import KnowledgeLoader, KnowledgeValidationError


class InMemoryKnowledgeRepository:
    def __init__(self, loader: KnowledgeLoader) -> None:
        self._loader = loader
        self._documents_by_id: dict[str, KnowledgeDocument] | None = None

    def load(self, *, force_reload: bool = False) -> list[KnowledgeDocument]:
        if self._documents_by_id is None or force_reload:
            documents = self._loader.load()
            documents_by_id: dict[str, KnowledgeDocument] = {}
            for document in documents:
                if document.id in documents_by_id:
                    raise KnowledgeValidationError(f"Duplicate knowledge document id: {document.id}")
                documents_by_id[document.id] = document
            self._documents_by_id = documents_by_id

        return self.all()

    def all(self, *, include_deprecated: bool = False) -> list[KnowledgeDocument]:
        documents = self._loaded_documents()
        if include_deprecated:
            return documents
        return [document for document in documents if document.status != KnowledgeDocumentStatus.DEPRECATED]

    def get(self, document_id: str) -> KnowledgeDocument | None:
        return self._loaded_documents_by_id().get(document_id)

    def by_domain(self, domain: KnowledgeDocumentDomain | str) -> list[KnowledgeDocument]:
        normalized_domain = KnowledgeDocumentDomain(domain)
        return [document for document in self.all() if document.domain == normalized_domain]

    def by_tag(self, tag: str) -> list[KnowledgeDocument]:
        return [document for document in self.all() if tag in document.tags]

    def _loaded_documents_by_id(self) -> dict[str, KnowledgeDocument]:
        if self._documents_by_id is None:
            self.load()
        assert self._documents_by_id is not None
        return self._documents_by_id

    def _loaded_documents(self) -> list[KnowledgeDocument]:
        return sorted(
            self._loaded_documents_by_id().values(),
            key=lambda document: (-document.priority, document.id),
        )
