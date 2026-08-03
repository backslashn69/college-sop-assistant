from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(
    title="YWCC SOP Assistant API",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        description="The SOP question submitted by the user",
    )


class ChatResponse(BaseModel):
    answer: str
    source: str | None = None


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "YWCC SOP Assistant API is running",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(
        answer=(
            "The backend received your question:\n\n"
            f'"{request.question}"\n\n'
            "The SOP retrieval system will be connected here."
        ),
        source="Registrar SOP v3.2 • Section 4.1 • Page 18",
    )