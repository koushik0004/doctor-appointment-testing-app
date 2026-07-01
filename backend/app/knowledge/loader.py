from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

from pydantic import ValidationError

from app.knowledge.documents import KnowledgeDocument, KnowledgeDocumentSourceType


class KnowledgeValidationError(ValueError):
    """Raised when a knowledge source cannot be normalized into the schema."""


class KnowledgeLoader(Protocol):
    def load(self) -> list[KnowledgeDocument]:
        """Load all configured knowledge documents."""

    def load_path(self, path: Path) -> KnowledgeDocument:
        """Load and validate one Markdown or JSON knowledge document."""

    def validate(self, document: KnowledgeDocument) -> None:
        """Raise when a document violates repository-level constraints."""


class FileSystemKnowledgeLoader:
    def __init__(self, root: Path) -> None:
        self.root = root

    def load(self) -> list[KnowledgeDocument]:
        documents: list[KnowledgeDocument] = []
        seen_ids: set[str] = set()

        for path in sorted(self.root.rglob("*")):
            if (
                not path.is_file()
                or path.name == "README.md"
                or path.suffix.lower() not in {".md", ".json"}
            ):
                continue

            document = self.load_path(path)
            if document.id in seen_ids:
                raise KnowledgeValidationError(f"Duplicate knowledge document id: {document.id}")
            seen_ids.add(document.id)
            documents.append(document)

        return documents

    def load_path(self, path: Path) -> KnowledgeDocument:
        if path.suffix.lower() == ".md":
            document = self._load_markdown(path)
        elif path.suffix.lower() == ".json":
            document = self._load_json(path)
        else:
            raise KnowledgeValidationError(f"Unsupported knowledge source type: {path}")

        self.validate(document)
        return document

    def validate(self, document: KnowledgeDocument) -> None:
        if isinstance(document.content, str) and not document.content.strip():
            raise KnowledgeValidationError(f"Knowledge document content is empty: {document.id}")
        if isinstance(document.content, dict) and not document.content:
            raise KnowledgeValidationError(f"Knowledge document content is empty: {document.id}")

    def _load_markdown(self, path: Path) -> KnowledgeDocument:
        text = path.read_text(encoding="utf-8")
        metadata, body = _split_markdown_front_matter(text, path)
        payload = {
            **metadata,
            "source_type": KnowledgeDocumentSourceType.MARKDOWN,
            "source_path": _source_path(path, self.root),
            "content": body.strip(),
        }
        return _validate_payload(payload, path)

    def _load_json(self, path: Path) -> KnowledgeDocument:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise KnowledgeValidationError(f"Invalid JSON knowledge source {path}: {exc.msg}") from exc

        if not isinstance(payload, dict):
            raise KnowledgeValidationError(f"JSON knowledge source must be an object: {path}")

        payload = {
            **payload,
            "source_type": KnowledgeDocumentSourceType.JSON,
            "source_path": _source_path(path, self.root),
        }
        return _validate_payload(payload, path)


def _split_markdown_front_matter(text: str, path: Path) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise KnowledgeValidationError(f"Markdown knowledge source is missing front matter: {path}")

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break

    if end_index is None:
        raise KnowledgeValidationError(f"Markdown knowledge source has unterminated front matter: {path}")

    metadata = _parse_front_matter(lines[1:end_index], path)
    body = "\n".join(lines[end_index + 1 :])
    return metadata, body


def _parse_front_matter(lines: list[str], path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    current_list_key: str | None = None
    current_object_key: str | None = None
    current_object_list_key: str | None = None

    for raw_line in lines:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if line.startswith("- "):
            value = _parse_scalar(line[2:].strip())
            if current_object_key and current_object_list_key:
                root[current_object_key][current_object_list_key].append(value)
            elif current_list_key:
                root[current_list_key].append(value)
            else:
                raise KnowledgeValidationError(f"Front matter list item has no parent key in {path}")
            continue

        if ":" not in line:
            raise KnowledgeValidationError(f"Unsupported front matter line in {path}: {raw_line}")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        if indent == 0:
            current_object_key = None
            current_object_list_key = None
            if raw_value == "":
                if key == "prompt_hints":
                    root[key] = {}
                    current_object_key = key
                else:
                    root[key] = []
                    current_list_key = key
            elif raw_value == "[]":
                root[key] = []
                current_list_key = key
            else:
                root[key] = _parse_scalar(raw_value)
                current_list_key = None
            continue

        if current_object_key is None:
            raise KnowledgeValidationError(f"Nested front matter key has no parent in {path}: {raw_line}")

        if raw_value in {"", "[]"}:
            root[current_object_key][key] = []
            current_object_list_key = key
        else:
            root[current_object_key][key] = _parse_scalar(raw_value)
            current_object_list_key = None

    return root


def _parse_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None"}:
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        return [_parse_scalar(item.strip()) for item in value[1:-1].split(",") if item.strip()]
    try:
        return int(value)
    except ValueError:
        return value


def _source_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _validate_payload(payload: dict[str, Any], path: Path) -> KnowledgeDocument:
    try:
        return KnowledgeDocument.model_validate(payload)
    except ValidationError as exc:
        raise KnowledgeValidationError(f"Invalid knowledge document {path}: {exc}") from exc
