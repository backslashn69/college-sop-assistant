from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from document_service import (
    build_sop_chunks,
    load_all_sops,
)

from llm_service import generate_grounded_answer

from retrieval_service import (
    build_precise_answer,
    find_best_sop_chunks,
)


app = FastAPI(
    title="YWCC SOP Assistant API",
    version="1.0.0",
)


INSUFFICIENT_ANSWER = (
    "I could not find enough information "
    "in the available SOP documents."
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
        cleaned_question = (
            request.question.strip()
        )

        if not cleaned_question:
            raise HTTPException(
                status_code=422,
                detail=(
                    "The question cannot "
                    "be empty."
                ),
            )

        sop_pages = load_all_sops()

        sop_chunks = build_sop_chunks(
            sop_pages
        )

        matching_chunks = (
            find_best_sop_chunks(
                cleaned_question,
                sop_chunks,
            )
        )

        if not matching_chunks:
            return ChatResponse(
                answer=INSUFFICIENT_ANSWER,
                source=None,
            )


        answer_chunks = matching_chunks[:2]

        primary_chunk = answer_chunks[0]

        section_type = str(
            primary_chunk.get(
                "type",
                "section",
            )
        )

        if section_type == "procedure":
            # Procedures must remain deterministic so that
            # steps, warnings, and ordering are preserved.
            answer = build_precise_answer(
                cleaned_question,
                [primary_chunk],
            )

        else:
            try:
                # Groq is used for non-procedure questions
                # that benefit from a concise explanation.
                answer = await generate_grounded_answer(
                    cleaned_question,
                    answer_chunks,
                )

            except Exception as error:
                print(
                    "Groq generation failed:",
                    error,
                )

                answer = build_precise_answer(
                    cleaned_question,
                    answer_chunks,
                )

        if not answer:
            return ChatResponse(
                answer=INSUFFICIENT_ANSWER,
                source=None,
            )

        if answer.strip() == INSUFFICIENT_ANSWER:
            return ChatResponse(
                answer=INSUFFICIENT_ANSWER,
                source=None,
            )

        sources: list[str] = []

        for chunk in answer_chunks:
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
                page_label = (
                    f"Page {page_start}"
                )
            else:
                page_label = (
                    f"Pages {page_start}-"
                    f"{page_end}"
                )

            source = (
                f'{chunk["document"]} '
                f'• {chunk["title"]} '
                f'• {page_label}'
            )

            if source not in sources:
                sources.append(source)

        return ChatResponse(
            answer=answer.strip(),
            source=" | ".join(sources),
        )

    except HTTPException:
        raise

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
                "Unable to process the SOP "
                f"question: {error}"
            ),
        ) from error