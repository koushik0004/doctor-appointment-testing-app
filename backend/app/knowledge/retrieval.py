from __future__ import annotations

import re
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from app.knowledge.documents import KnowledgeDocument
from app.knowledge.repository import InMemoryKnowledgeRepository
from app.llm.runtime_trace import AIRuntimeTraceSession


_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "about",
    "a",
    "accepted",
    "after",
    "all",
    "an",
    "and",
    "are",
    "appointment",
    "appointments",
    "available",
    "before",
    "can",
    "consultation",
    "doctor",
    "doctors",
    "do",
    "for",
    "have",
    "help",
    "how",
    "i",
    "is",
    "it",
    "me",
    "method",
    "methods",
    "my",
    "need",
    "of",
    "online",
    "on",
    "provide",
    "provided",
    "provides",
    "some",
    "specialization",
    "specializations",
    "support",
    "slot",
    "slots",
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

    def retrieve_top_match(
        self,
        query: str,
        *,
        runtime_trace: AIRuntimeTraceSession | None = None,
    ) -> KnowledgeRetrievalMatch | None:
        started_at = perf_counter()
        if runtime_trace is not None:
            runtime_trace.update_stage(
                "vectorless_rag",
                {
                    "retrieval_started": True,
                    "retrieval_completed": False,
                },
            )

        try:
            query_terms = _tokenize(query)
            normalized_query = _normalize_free_text(query)
            if not query_terms and not normalized_query:
                return None

            matches = [
                match
                for document in self._repository.all()
                if (match := self._score_document(document, query_terms, normalized_query)) is not None
            ]
            if not matches:
                return None

            match = sorted(
                matches,
                key=lambda match: (-match.score, -match.document.priority, match.document.id),
            )[0]
            if runtime_trace is not None:
                runtime_trace.update_stage(
                    "vectorless_rag",
                    {
                        "matched_document": match.document.id,
                        "matched_title": match.document.title,
                        "score": match.score,
                        "matched_terms": list(match.matched_terms),
                    },
                )
            return match
        except Exception as exc:
            if runtime_trace is not None:
                runtime_trace.record_exception("vectorless_rag", exc)
            raise
        finally:
            if runtime_trace is not None:
                runtime_trace.update_stage(
                    "vectorless_rag",
                    {
                        "retrieval_completed": True,
                        "duration_ms": round((perf_counter() - started_at) * 1000, 3),
                    },
                )

    def _score_document(
        self,
        document: KnowledgeDocument,
        query_terms: tuple[str, ...],
        normalized_query: str,
    ) -> KnowledgeRetrievalMatch | None:
        title_terms = set(_tokenize(document.title))
        alias_terms = _document_alias_terms(document)
        keyword_terms = _document_terms(document.keywords)
        synonym_terms = _document_terms(document.synonyms)
        category_terms = _tokenize_scalar(document.category)
        body_terms = _document_body_terms(document)
        title_phrase_labels = _matching_phrase_labels(normalized_query, [document.title])
        alias_phrase_labels = _matching_phrase_labels(normalized_query, document.aliases)
        keyword_phrase_labels = _matching_phrase_labels(normalized_query, document.keywords)
        synonym_phrase_labels = _matching_phrase_labels(normalized_query, document.synonyms)
        category_phrase_labels = _matching_phrase_labels(
            normalized_query,
            [document.category] if document.category else [],
        )
        title_phrase_match = bool(title_phrase_labels)
        alias_phrase_match = bool(alias_phrase_labels)
        keyword_phrase_match = bool(keyword_phrase_labels)
        synonym_phrase_match = bool(synonym_phrase_labels)
        category_phrase_match = bool(category_phrase_labels)

        matched_title_terms = set(query_terms).intersection(title_terms)
        matched_alias_terms = set(query_terms).intersection(alias_terms)
        matched_keyword_terms = set(query_terms).intersection(keyword_terms)
        matched_synonym_terms = set(query_terms).intersection(synonym_terms)
        matched_category_terms = set(query_terms).intersection(category_terms)
        matched_body_terms = set(query_terms).intersection(body_terms)
        if not any(
            (
                title_phrase_match,
                alias_phrase_match,
                keyword_phrase_match,
                synonym_phrase_match,
                category_phrase_match,
                matched_title_terms,
                matched_alias_terms,
                matched_keyword_terms,
                matched_synonym_terms,
                matched_category_terms,
                matched_body_terms,
            )
        ):
            return None

        score = (
            (120 if title_phrase_match else 0)
            + (140 if alias_phrase_match else 0)
            + (100 if keyword_phrase_match else 0)
            + (80 if synonym_phrase_match else 0)
            + (40 if category_phrase_match else 0)
            + (len(matched_title_terms) * 50)
            + (len(matched_alias_terms) * 45)
            + (len(matched_keyword_terms) * 30)
            + (len(matched_synonym_terms) * 20)
            + (len(matched_category_terms) * 10)
            + (len(matched_body_terms) * 5)
        )
        matched_terms = tuple(
            sorted(
                matched_title_terms
                .union(matched_alias_terms)
                .union(matched_keyword_terms)
                .union(matched_synonym_terms)
                .union(matched_category_terms)
                .union(matched_body_terms)
                .union(title_phrase_labels)
                .union(alias_phrase_labels)
                .union(keyword_phrase_labels)
                .union(synonym_phrase_labels)
                .union(category_phrase_labels)
            )
        )
        return KnowledgeRetrievalMatch(document=document, score=score, matched_terms=matched_terms)


def _document_alias_terms(document: KnowledgeDocument) -> set[str]:
    return _document_terms(document.aliases)


def _document_terms(values: list[str]) -> set[str]:
    return set(_tokenize(" ".join(values)))


def _tokenize_scalar(value: str | None) -> set[str]:
    if not value:
        return set()
    return set(_tokenize(value))


def _matching_phrase_labels(query: str, phrases: list[str]) -> set[str]:
    if not query:
        return set()
    matches: set[str] = set()
    for phrase in phrases:
        normalized_phrase = _normalize_free_text(phrase)
        if normalized_phrase and normalized_phrase in query:
            matches.add(normalized_phrase)
    return matches


def _document_body_terms(document: KnowledgeDocument) -> set[str]:
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


def _normalize_free_text(text: str) -> str:
    return " ".join(_TOKEN_PATTERN.findall(text.lower()))


def _normalize_token(token: str) -> str:
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token
