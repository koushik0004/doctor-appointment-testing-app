from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )


class ChatResponse(BaseModel):
    response: str
