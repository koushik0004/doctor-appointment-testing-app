from typing import Protocol

from app.schemas.chat import ChatRequest, ChatResponse


class ChatResponder(Protocol):
    def generate(self, message: str) -> str:
        ...


class RuleBasedChatResponder:
    def __init__(self) -> None:
        self._reply_rules: tuple[tuple[tuple[str, ...], str], ...] = (
            (("hello", "hi", "hey"), "Hello, I am your AI Assistant."),
            (("cardiologist",), "I can help you find a cardiologist."),
            (("dermatologist",), "I can help you find a dermatologist."),
            (("pediatrician",), "I can help you find a pediatrician."),
            (
                ("book", "appointment"),
                "I can help you book an appointment with an available doctor.",
            ),
            (
                ("schedule", "time", "slot"),
                "I can help you check available schedules and appointment times.",
            ),
        )

    def generate(self, message: str) -> str:
        normalized_message = message.strip().lower()

        for keywords, reply in self._reply_rules:
            if any(keyword in normalized_message for keyword in keywords):
                return reply

        return "I can help with doctors, schedules, and booking questions."


def create_chat_response(
    request: ChatRequest,
    responder: ChatResponder | None = None,
) -> ChatResponse:
    chat_responder = responder or RuleBasedChatResponder()
    return ChatResponse(response=chat_responder.generate(request.message))
