from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.knowledge.documents import KnowledgeDocument
from app.knowledge.repository import InMemoryKnowledgeRepository


_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "do",
    "for",
    "help",
    "how",
    "i",
    "is",
    "it",
    "me",
    "my",
    "need",
    "of",
    "on",
    "some",
    "the",
    "to",
    "what",
    "with",
    "you",
}


@dataclass(frozen=True)
class KnowledgeRetrievalMatch:
    document: KnowledgeDocument
    score: int
    matched_terms: tuple[str, ...]


class KnowledgeRetrievalService:
    """Deterministic keyword/title retrieval over the loaded knowledge repository."""

    def __init__(self, repository: InMemoryKnowledgeRepository) -> None:
        self._repository = repository

    def retrieve_top(self, query: str) -> KnowledgeDocument | None:
        match = self.retrieve_top_match(query)
        if match is None:
            return None
        return match.document

    def retrieve_top_match(self, query: str) -> KnowledgeRetrievalMatch | None:
        query_terms = _tokenize(query)
        if not query_terms:
            return None

        matches = [
            match
            for document in self._repository.all()
            if (match := self._score_document(document, query_terms)) is not None
        ]
        if not matches:
            return None

        return sorted(
            matches,
            key=lambda match: (-match.score, -match.document.priority, match.document.id),
        )[0]

    def _score_document(
        self,
        document: KnowledgeDocument,
        query_terms: tuple[str, ...],
    ) -> KnowledgeRetrievalMatch | None:
        title_terms = set(_tokenize(document.title))
        keyword_terms = _document_keyword_terms(document)

        matched_title_terms = set(query_terms).intersection(title_terms)
        matched_keyword_terms = set(query_terms).intersection(keyword_terms)
        if not matched_title_terms and not matched_keyword_terms:
            return None

        # Title hits should beat content-only keyword hits for direct user questions.
        score = (len(matched_title_terms) * 10) + len(matched_keyword_terms)
        matched_terms = tuple(sorted(matched_title_terms.union(matched_keyword_terms)))
        return KnowledgeRetrievalMatch(document=document, score=score, matched_terms=matched_terms)


def _document_keyword_terms(document: KnowledgeDocument) -> set[str]:
    text_parts = [
        document.summary,
        *_stringify_content(document.content),
        *document.tags,
    ]
    return set(_tokenize(" ".join(text_parts)))


def _stringify_content(content: str | dict[str, Any]) -> list[str]:
    if isinstance(content, str):
        return [content]

    values: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, dict):
            for nested_value in value.values():
                visit(nested_value)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(content)
    return values


def _tokenize(text: str) -> tuple[str, ...]:
    tokens = [_normalize_token(token) for token in _TOKEN_PATTERN.findall(text.lower())]
    return tuple(token for token in tokens if token and token not in _STOPWORDS)


def _normalize_token(token: str) -> str:
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token
