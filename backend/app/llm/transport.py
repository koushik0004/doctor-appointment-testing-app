from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from app.llm.config import LLMProviderConfiguration, LLMProviderName
from app.llm.providers import ProviderPayload

logger = logging.getLogger(__name__)

DEFAULT_CLAUDE_MAX_TOKENS = 1024


class LLMTransportError(RuntimeError):
    """Normalized runtime error raised by production provider transports."""

    def __init__(
        self,
        message: str,
        *,
        provider_name: str,
        error_code: str,
        status_code: int | None = None,
        request_id: str | None = None,
        retryable: bool = False,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.provider_name = provider_name
        self.error_code = error_code
        self.status_code = status_code
        self.request_id = request_id
        self.retryable = retryable
        self.metadata = dict(metadata or {})


@dataclass(frozen=True)
class LLMTransportActivationSnapshot:
    available: bool
    transport_name: str
    provider_name: str
    diagnostics: tuple[dict[str, Any], ...] = ()
    metadata: Mapping[str, Any] | None = None


class ClaudeTransport:
    """Production Anthropic-backed transport for Claude requests."""

    def __init__(
        self,
        configuration: LLMProviderConfiguration,
        *,
        client: Any | None = None,
        client_factory: Callable[[LLMProviderConfiguration], Any] | None = None,
        sdk_loader: Callable[[], Any] | None = None,
    ) -> None:
        if configuration.provider_name is not LLMProviderName.CLAUDE:
            raise ValueError("ClaudeTransport requires Claude provider configuration.")

        self._configuration = configuration
        self._client = client
        self._client_factory = (
            client_factory if client_factory is not None else self._build_default_client
        )
        self._sdk_loader = sdk_loader if sdk_loader is not None else self._load_sdk

    def invoke(self, request: ProviderPayload) -> ProviderPayload:
        start = time.perf_counter()
        request_id: str | None = None
        response_id: str | None = None
        status_code: int | None = None

        try:
            client = self._get_client()
            create_params = self._build_create_params(request)
            raw_response = self._invoke_messages_create(client, create_params)
            message = raw_response["message"]
            request_id = raw_response["request_id"]
            status_code = raw_response["status_code"]
            response_id = self._coerce_optional_str(getattr(message, "id", None))

            payload = self._translate_sdk_response(
                message,
                request_id=request_id,
                response_id=response_id,
                status_code=status_code,
                latency_ms=self._compute_latency_ms(start),
            )
            self._log_success(
                payload=payload,
                model=str(payload.get("model") or request.get("model") or ""),
                request_id=request_id,
                response_id=response_id,
                status_code=status_code,
                latency_ms=self._compute_latency_ms(start),
            )
            return payload
        except Exception as exc:
            normalized = self._map_error(
                exc,
                request=request,
                request_id=request_id,
                status_code=status_code,
                latency_ms=self._compute_latency_ms(start),
            )
            self._log_failure(
                model=str(request.get("model") or ""),
                request_id=normalized.request_id,
                response_id=response_id,
                status_code=normalized.status_code,
                latency_ms=self._compute_latency_ms(start),
                error=normalized,
            )
            raise normalized from exc

    def get_activation_snapshot(self) -> LLMTransportActivationSnapshot:
        diagnostics: list[dict[str, Any]] = []
        available = True

        if self._configuration.api_key is None or not self._configuration.api_key.get_secret_value().strip():
            diagnostics.append(
                {
                    "code": "transport_authentication_missing",
                    "message": "Claude transport is missing an API key.",
                    "severity": "error",
                    "blocking": True,
                }
            )
            available = False

        try:
            self._sdk_loader()
        except Exception as exc:
            diagnostics.append(
                {
                    "code": "transport_sdk_unavailable",
                    "message": str(exc),
                    "severity": "error",
                    "blocking": True,
                }
            )
            available = False

        return LLMTransportActivationSnapshot(
            available=available,
            transport_name=self.__class__.__name__,
            provider_name=self._configuration.provider_name.value,
            diagnostics=tuple(diagnostics),
            metadata={
                "base_url_configured": self._configuration.base_url is not None,
                "timeout_seconds": self._configuration.timeout_seconds,
                "max_retries": self._configuration.max_retries,
            },
        )

    def _get_client(self) -> Any:
        if self._client is None:
            self._client = self._client_factory(self._configuration)
        return self._client

    def _build_default_client(self, configuration: LLMProviderConfiguration) -> Any:
        sdk = self._sdk_loader()
        return sdk.Anthropic(
            api_key=configuration.api_key.get_secret_value() if configuration.api_key else None,
            base_url=configuration.base_url,
            timeout=configuration.timeout_seconds,
            max_retries=configuration.max_retries,
        )

    def _load_sdk(self) -> Any:
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError(
                "Anthropic SDK is not installed. Add the 'anthropic' package to enable Claude transport."
            ) from exc
        return anthropic

    def _invoke_messages_create(
        self,
        client: Any,
        create_params: dict[str, Any],
    ) -> dict[str, Any]:
        messages_api = getattr(client, "messages")
        raw_api = getattr(messages_api, "with_raw_response", None)
        if raw_api is not None and hasattr(raw_api, "create"):
            raw_response = raw_api.create(**create_params)
            parsed = raw_response.parse() if hasattr(raw_response, "parse") else raw_response
            headers = getattr(raw_response, "headers", {}) or {}
            status_code = getattr(raw_response, "status_code", None)
            request_id = headers.get("request-id") or headers.get("x-request-id")
            return {
                "message": parsed,
                "request_id": self._coerce_optional_str(request_id),
                "status_code": status_code if isinstance(status_code, int) else None,
            }

        message = messages_api.create(**create_params)
        return {
            "message": message,
            "request_id": self._coerce_optional_str(getattr(message, "_request_id", None)),
            "status_code": None,
        }

    def _build_create_params(self, request: ProviderPayload) -> dict[str, Any]:
        generation_budget = (
            dict(request.get("generation_budget"))
            if isinstance(request.get("generation_budget"), dict)
            else {}
        )

        params: dict[str, Any] = {
            "model": str(request["model"]),
            "messages": self._build_messages(request.get("messages")),
            "max_tokens": self._resolve_max_tokens(request, generation_budget),
            "metadata": self._build_metadata(request),
        }

        if isinstance(request.get("system"), str) and request["system"].strip():
            params["system"] = request["system"]
        if isinstance(request.get("temperature"), (int, float)):
            params["temperature"] = request["temperature"]
        if isinstance(request.get("top_p"), (int, float)):
            params["top_p"] = request["top_p"]
        if isinstance(request.get("stop_sequences"), list) and request["stop_sequences"]:
            params["stop_sequences"] = list(request["stop_sequences"])

        thinking = self._build_thinking(request, generation_budget)
        if thinking is not None:
            params["thinking"] = thinking

        tools = self._build_tools(request.get("tools"))
        if tools:
            params["tools"] = tools

        tool_choice = self._build_tool_choice(request.get("tool_choice"))
        if tool_choice is not None:
            params["tool_choice"] = tool_choice

        return params

    def _resolve_max_tokens(
        self,
        request: ProviderPayload,
        generation_budget: Mapping[str, Any],
    ) -> int:
        max_tokens = request.get("max_tokens")
        if isinstance(max_tokens, int) and max_tokens > 0:
            return max_tokens

        budget_max_tokens = generation_budget.get("max_tokens")
        if isinstance(budget_max_tokens, int) and budget_max_tokens > 0:
            return budget_max_tokens

        return DEFAULT_CLAUDE_MAX_TOKENS

    def _build_metadata(self, request: ProviderPayload) -> dict[str, str]:
        metadata = (
            dict(request.get("adapter_metadata", {}).get("metadata", {}))
            if isinstance(request.get("adapter_metadata"), dict)
            else {}
        )
        return {
            str(key): str(value)
            for key, value in metadata.items()
            if value is not None
        }

    def _build_thinking(
        self,
        request: ProviderPayload,
        generation_budget: Mapping[str, Any],
    ) -> dict[str, Any] | None:
        thinking = (
            dict(request.get("thinking"))
            if isinstance(request.get("thinking"), dict)
            else {}
        )
        budget_thinking = (
            dict(generation_budget.get("thinking"))
            if isinstance(generation_budget.get("thinking"), dict)
            else {}
        )

        payload = {**budget_thinking, **thinking}
        if not payload:
            return None

        resolved: dict[str, Any] = {}
        if isinstance(payload.get("effort"), str):
            resolved["effort"] = payload["effort"]
        if payload.get("include_summary") is not None:
            resolved["include_summary"] = bool(payload["include_summary"])
        return resolved or None

    def _build_messages(self, raw_messages: Any) -> list[dict[str, Any]]:
        if not isinstance(raw_messages, list):
            raise LLMTransportError(
                "Claude transport requires a non-empty messages list.",
                provider_name="claude",
                error_code="invalid_request",
            )

        messages: list[dict[str, Any]] = []
        for raw_message in raw_messages:
            if not isinstance(raw_message, dict):
                continue
            role = str(raw_message.get("role") or "user")
            if role == "tool":
                messages.append(
                    {
                        "role": "user",
                        "content": self._build_tool_result_blocks(raw_message),
                    }
                )
                continue
            messages.append(
                {
                    "role": "assistant" if role == "assistant" else "user",
                    "content": self._build_content_blocks(raw_message),
                }
            )
        if not messages:
            raise LLMTransportError(
                "Claude transport requires at least one message.",
                provider_name="claude",
                error_code="invalid_request",
            )
        return messages

    def _build_content_blocks(self, raw_message: Mapping[str, Any]) -> list[dict[str, Any]] | str:
        blocks: list[dict[str, Any]] = []
        content = raw_message.get("content")
        if isinstance(content, str) and content.strip():
            blocks.append({"type": "text", "text": content})

        tool_calls = raw_message.get("tool_calls")
        if isinstance(tool_calls, list):
            for tool_call in tool_calls:
                if not isinstance(tool_call, dict):
                    continue
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": str(tool_call.get("id") or tool_call.get("call_id") or ""),
                        "name": str(tool_call.get("name") or tool_call.get("tool_name") or ""),
                        "input": (
                            dict(tool_call.get("arguments"))
                            if isinstance(tool_call.get("arguments"), dict)
                            else {}
                        ),
                    }
                )

        if len(blocks) == 1 and blocks[0]["type"] == "text":
            return blocks[0]["text"]
        return blocks

    def _build_tool_result_blocks(self, raw_message: Mapping[str, Any]) -> list[dict[str, Any]]:
        content = raw_message.get("content")
        text_content = str(content) if content is not None else ""
        return [
            {
                "type": "tool_result",
                "tool_use_id": str(raw_message.get("tool_call_id") or ""),
                "content": text_content,
            }
        ]

    def _build_tools(self, raw_tools: Any) -> list[dict[str, Any]]:
        if not isinstance(raw_tools, list):
            return []
        tools: list[dict[str, Any]] = []
        for raw_tool in raw_tools:
            if not isinstance(raw_tool, dict):
                continue
            tool_payload = {
                "name": str(raw_tool.get("name") or ""),
                "description": raw_tool.get("description"),
                "input_schema": (
                    dict(raw_tool.get("input_schema"))
                    if isinstance(raw_tool.get("input_schema"), dict)
                    else {}
                ),
            }
            tools.append(tool_payload)
        return tools

    def _build_tool_choice(self, raw_tool_choice: Any) -> dict[str, Any] | None:
        if not isinstance(raw_tool_choice, dict):
            return None
        mode = str(raw_tool_choice.get("mode") or "").lower()
        if mode == "auto":
            return {"type": "auto"}
        if mode == "none":
            return {"type": "none"}
        if mode == "required":
            return {"type": "any"}
        if mode == "named" and raw_tool_choice.get("tool_name"):
            return {"type": "tool", "name": str(raw_tool_choice["tool_name"])}
        return None

    def _translate_sdk_response(
        self,
        message: Any,
        *,
        request_id: str | None,
        response_id: str | None,
        status_code: int | None,
        latency_ms: int,
    ) -> ProviderPayload:
        content_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        citations: list[dict[str, Any]] = []
        thinking_summary: str | None = None

        for block in getattr(message, "content", []) or []:
            block_type = self._coerce_optional_str(getattr(block, "type", None))
            if block_type == "text":
                text = self._coerce_optional_str(getattr(block, "text", None)) or ""
                if text:
                    content_parts.append(text)
                citations.extend(self._extract_citations(block))
                continue
            if block_type == "thinking":
                thinking_value = self._coerce_optional_str(getattr(block, "thinking", None))
                if thinking_value:
                    thinking_summary = thinking_value
                continue
            if block_type == "tool_use":
                tool_calls.append(
                    {
                        "tool_use_id": self._coerce_optional_str(getattr(block, "id", None)) or "",
                        "tool_name": self._coerce_optional_str(getattr(block, "name", None)) or "",
                        "arguments": dict(getattr(block, "input", {}) or {}),
                    }
                )

        usage = getattr(message, "usage", None)
        payload: ProviderPayload = {
            "content": "\n".join(part for part in content_parts if part).strip(),
            "stop_reason": self._coerce_optional_str(getattr(message, "stop_reason", None)),
            "model": self._coerce_optional_str(getattr(message, "model", None)),
            "usage": {
                "input_tokens": getattr(usage, "input_tokens", None),
                "output_tokens": getattr(usage, "output_tokens", None),
            },
            "tool_calls": tool_calls,
            "provider_metadata": {
                "request_id": request_id,
                "response_id": response_id,
                "status_code": status_code,
                "latency_ms": latency_ms,
            },
            "model_metadata": {
                "role": self._coerce_optional_str(getattr(message, "role", None)),
                "type": self._coerce_optional_str(getattr(message, "type", None)),
            },
            "metadata": {},
        }
        if thinking_summary is not None:
            payload["thinking_summary"] = thinking_summary
        if citations:
            payload["metadata"] = {"citations": citations}
        return payload

    def _extract_citations(self, block: Any) -> list[dict[str, Any]]:
        raw_citations = getattr(block, "citations", None)
        if not isinstance(raw_citations, list):
            return []
        citations: list[dict[str, Any]] = []
        for citation in raw_citations:
            citations.append(
                {
                    "label": self._coerce_optional_str(getattr(citation, "title", None)),
                    "url": self._coerce_optional_str(getattr(citation, "url", None)),
                    "excerpt": self._coerce_optional_str(getattr(citation, "cited_text", None)),
                }
            )
        return citations

    def _map_error(
        self,
        exc: Exception,
        *,
        request: ProviderPayload,
        request_id: str | None,
        status_code: int | None,
        latency_ms: int,
    ) -> LLMTransportError:
        if isinstance(exc, LLMTransportError):
            return exc

        anthropic_status = getattr(exc, "status_code", None)
        anthropic_request_id = self._coerce_optional_str(getattr(exc, "request_id", None))
        resolved_status_code = anthropic_status if isinstance(anthropic_status, int) else status_code
        resolved_request_id = anthropic_request_id or request_id

        error_code = "sdk_exception"
        retryable = False
        if type(exc).__name__ == "AuthenticationError" or resolved_status_code == 401:
            error_code = "authentication_error"
        elif type(exc).__name__ == "PermissionError" or resolved_status_code == 403:
            error_code = "permission_denied"
        elif type(exc).__name__ == "NotFoundError" or resolved_status_code == 404:
            error_code = "not_found"
        elif type(exc).__name__ == "RateLimitError" or resolved_status_code == 429:
            error_code = "rate_limited"
            retryable = True
        elif type(exc).__name__ in {"APITimeoutError", "TimeoutException"} or resolved_status_code == 408:
            error_code = "timeout"
            retryable = True
        elif type(exc).__name__ == "APIConnectionError":
            error_code = "network_error"
            retryable = True
        elif resolved_status_code == 500:
            error_code = "server_error"
            retryable = True
        elif type(exc).__name__ == "OverloadedError" or resolved_status_code == 503:
            error_code = "service_unavailable"
            retryable = True
        elif resolved_status_code is not None and 500 <= resolved_status_code <= 599:
            error_code = "server_error"
            retryable = True

        return LLMTransportError(
            str(exc),
            provider_name="claude",
            error_code=error_code,
            status_code=resolved_status_code,
            request_id=resolved_request_id,
            retryable=retryable,
            metadata={
                "model": request.get("model"),
                "latency_ms": latency_ms,
            },
        )

    def _log_success(
        self,
        *,
        payload: ProviderPayload,
        model: str,
        request_id: str | None,
        response_id: str | None,
        status_code: int | None,
        latency_ms: int,
    ) -> None:
        usage = payload.get("usage")
        logger.info(
            "llm_transport_success",
            extra={
                "provider": "claude",
                "model": model,
                "request_id": request_id,
                "response_id": response_id,
                "latency_ms": latency_ms,
                "input_tokens": usage.get("input_tokens") if isinstance(usage, dict) else None,
                "output_tokens": usage.get("output_tokens") if isinstance(usage, dict) else None,
                "finish_reason": payload.get("stop_reason"),
                "status_code": status_code,
            },
        )

    def _log_failure(
        self,
        *,
        model: str,
        request_id: str | None,
        response_id: str | None,
        status_code: int | None,
        latency_ms: int,
        error: LLMTransportError,
    ) -> None:
        logger.warning(
            "llm_transport_failure",
            extra={
                "provider": "claude",
                "model": model,
                "request_id": request_id,
                "response_id": response_id,
                "latency_ms": latency_ms,
                "input_tokens": None,
                "output_tokens": None,
                "finish_reason": None,
                "status_code": status_code,
                "error_code": error.error_code,
                "retryable": error.retryable,
            },
        )

    def _compute_latency_ms(self, start: float) -> int:
        return int((time.perf_counter() - start) * 1000)

    def _coerce_optional_str(self, value: Any) -> str | None:
        if value is None:
            return None
        coerced = str(value).strip()
        return coerced or None
