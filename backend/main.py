from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from document_service import (
    build_sop_chunks,
    load_all_sops,
)

from retrieval_service import (
    build_precise_answer,
    find_best_sop_chunks,
)


app = FastAPI(
    title="YWCC SOP Assistant API",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        description=(
            "The SOP question submitted "
            "by the user"
        ),
    )


class ChatResponse(BaseModel):
    answer: str
    source: str | None = None


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": (
            "YWCC SOP Assistant API "
            "is running"
        ),
    }


@app.get("/documents/status")
async def document_status() -> dict[
    str,
    int | str,
]:
    try:
        sop_pages = load_all_sops()

        sop_chunks = build_sop_chunks(
            sop_pages
        )

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
            "documents": len(
                document_names
            ),
            "pages": len(sop_pages),
            "chunks": len(sop_chunks),
            "characters": (
                total_characters
            ),
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
            detail=(
                "Unable to load SOP "
                f"documents: {error}"
            ),
        ) from error


@app.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:
    try:
        sop_pages = load_all_sops()

        sop_chunks = build_sop_chunks(
            sop_pages
        )

        matching_chunks = (
            find_best_sop_chunks(
                request.question,
                sop_chunks,
            )
        )

        if not matching_chunks:
            return ChatResponse(
                answer=(
                    "I could not find a "
                    "relevant procedure in "
                    "the available SOP "
                    "documents."
                ),
                source=None,
            )

        answer = build_precise_answer(
            request.question,
            matching_chunks,
        )

        if not answer:
            return ChatResponse(
                answer=(
                    "I found related SOP "
                    "content, but I could "
                    "not extract a precise "
                    "answer from it."
                ),
                source=None,
            )

        sources: list[str] = []

        for chunk in matching_chunks:
            page_start = int(
                chunk.get(
                    "page_start",
                    chunk["page"],
                )
            )

            page_end = int(
                chunk.get(
                    "page_end",
                    page_start,
                )
            )

            if page_start == page_end:
                page_label = f"Page {page_start}"
            else:
                page_label = (
                    f"Pages {page_start}-{page_end}"
                )

            source = (
                f'{chunk["document"]} '
                f'• {chunk["title"]} '
                f'• {page_label}'
            )

            if source not in sources:
                sources.append(source)

        return ChatResponse(
            answer=answer,
            source=" | ".join(
                sources[:2]
            ),
        )

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
            detail=(
                "Unable to search SOP "
                f"documents: {error}"
            ),
        ) from error