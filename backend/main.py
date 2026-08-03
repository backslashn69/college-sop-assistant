from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from document_service import load_all_sops



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

@app.get("/documents/status")
async def document_status() -> dict[str, int | str]:
    try:
        sop_pages = load_all_sops()

        document_names = {
            str(page["document"])
            for page in sop_pages
        }

        total_characters = sum(
            len(str(page["text"]))
            for page in sop_pages
        )

        return {
            "status": "loaded",
            "documents": len(document_names),
            "pages": len(sop_pages),
            "characters": total_characters,
        }

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load SOP documents: {error}",
        ) from error


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