from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeDocumentSourceType(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


class KnowledgeDocumentDomain(str, Enum):
    FAQ = "faq"
    POLICY = "policy"
    CAPABILITY = "capability"
    WORKFLOW_GUIDANCE = "workflow_guidance"
    SAFETY = "safety"


class KnowledgeDocumentAudience(str, Enum):
    PATIENT = "patient"
    ASSISTANT = "assistant"
    DEVELOPER = "developer"
    INTERNAL = "internal"


class KnowledgeDocumentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class KnowledgePromptHints(BaseModel):
    include_when_intents: list[str] = Field(default_factory=list)
    exclude_when_intents: list[str] = Field(default_factory=list)
    safe_to_quote: bool = False
    requires_domain_validation: bool = False
    max_context_chars: int | None = Field(default=None, gt=0)

    model_config = ConfigDict(str_strip_whitespace=True)


class KnowledgeDocument(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_type: KnowledgeDocumentSourceType
    source_path: str = Field(min_length=1)
    domain: KnowledgeDocumentDomain
    audience: KnowledgeDocumentAudience
    status: KnowledgeDocumentStatus
    version: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    priority: int = 0
    summary: str = Field(min_length=1)
    content: str | dict[str, Any]
    prompt_hints: KnowledgePromptHints | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(str_strip_whitespace=True)
