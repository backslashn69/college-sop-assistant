import re
from pathlib import Path
from uuid import uuid4

import os
import secrets

from fastapi import ( FastAPI, Header, HTTPException, File, UploadFile)
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from pypdf import PdfReader

from document_service import (
    SOP_DIRECTORY,
    clear_sop_cache,
    load_sop_index,
)

from llm_service import generate_grounded_answer

from retrieval_service import (
    build_precise_answer,
    find_best_sop_chunks,
    extract_keywords,
    is_procedure_question,
)

load_dotenv()

MAX_SOP_UPLOAD_BYTES = 20 * 1024 * 1024

ACCEPTED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/octet-stream",
}


def create_safe_pdf_filename(
    uploaded_filename: str | None,
) -> str:
    """
    Create a safe local PDF filename and prevent
    directory traversal through uploaded filenames.
    """
    if not uploaded_filename:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file has no filename.",
        )

    original_name = Path(
        uploaded_filename
    ).name.strip()

    original_path = Path(original_name)

    if original_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=415,
            detail="Only PDF files are accepted.",
        )

    safe_stem = re.sub(
        r"[^A-Za-z0-9._ -]+",
        "_",
        original_path.stem,
    ).strip(" ._")

    if not safe_stem:
        raise HTTPException(
            status_code=400,
            detail="The PDF filename is invalid.",
        )

    return f"{safe_stem}.pdf"

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
        sop_pages, sop_chunks = (
            load_sop_index() 
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

@app.post("/documents/reload")
async def reload_documents(
    x_admin_key: str | None = Header(
        default=None,
        alias="X-Admin-Key",
    ),
) -> dict[str, int | str]:
    """
    Clear the cached SOP index and rebuild it
    from the PDFs in backend/data/sops.
    """
    configured_key = os.getenv(
        "ADMIN_RELOAD_KEY"
    )

    if not configured_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "ADMIN_RELOAD_KEY is not "
                "configured on the backend."
            ),
        )

    if (
        not x_admin_key
        or not secrets.compare_digest(
            x_admin_key,
            configured_key,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin key.",
        )

    try:
        clear_sop_cache()

        sop_pages, sop_chunks = (
            load_sop_index()
        )

        document_names = {
            str(page["document"])
            for page in sop_pages
        }

        return {
            "status": "reloaded",
            "documents": len(
                document_names
            ),
            "pages": len(sop_pages),
            "chunks": len(sop_chunks),
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
                "Unable to reload SOP "
                f"documents: {error}"
            ),
        ) from error

@app.post("/documents/upload")
async def upload_sop_document(
    file: UploadFile = File(...),
    x_admin_key: str | None = Header(
        default=None,
        alias="X-Admin-Key",
    ),
) -> dict[str, int | str]:
    """
    Validate and save one searchable SOP PDF,
    then rebuild the cached SOP index.
    """
    configured_key = os.getenv(
        "ADMIN_RELOAD_KEY"
    )

    if not configured_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "ADMIN_RELOAD_KEY is not "
                "configured on the backend."
            ),
        )

    if (
        not x_admin_key
        or not secrets.compare_digest(
            x_admin_key,
            configured_key,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin key.",
        )

    safe_filename = create_safe_pdf_filename(
        file.filename
    )

    if (
        file.content_type
        and file.content_type
        not in ACCEPTED_PDF_CONTENT_TYPES
    ):
        raise HTTPException(
            status_code=415,
            detail="Only PDF files are accepted.",
        )

    SOP_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination_path = (
        SOP_DIRECTORY / safe_filename
    )

    if destination_path.exists():
        raise HTTPException(
            status_code=409,
            detail=(
                "A PDF with this filename "
                "already exists."
            ),
        )

    temporary_path = (
        SOP_DIRECTORY
        / f".upload-{uuid4().hex}.tmp"
    )

    saved_to_destination = False
    uploaded_size = 0

    try:
        with temporary_path.open("wb") as output:
            while True:
                data = await file.read(
                    1024 * 1024
                )

                if not data:
                    break

                uploaded_size += len(data)

                if (
                    uploaded_size
                    > MAX_SOP_UPLOAD_BYTES
                ):
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "The PDF exceeds the "
                            "20 MB upload limit."
                        ),
                    )

                output.write(data)

        if uploaded_size == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded PDF is empty.",
            )

        try:
            with temporary_path.open(
                "rb"
            ) as pdf_stream:
                signature = pdf_stream.read(5)

                if signature != b"%PDF-":
                    raise HTTPException(
                        status_code=415,
                        detail=(
                            "The uploaded file is "
                            "not a valid PDF."
                        ),
                    )

                pdf_stream.seek(0)

                reader = PdfReader(pdf_stream)

                if len(reader.pages) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "The PDF does not "
                            "contain any pages."
                        ),
                    )

                has_readable_text = False

                for page in reader.pages:
                    page_text = page.extract_text()

                    if (
                        page_text
                        and page_text.strip()
                    ):
                        has_readable_text = True
                        break

                if not has_readable_text:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "No readable text was "
                            "found in the PDF. "
                            "Scanned PDFs require "
                            "OCR before uploading."
                        ),
                    )

        except HTTPException:
            raise

        except Exception as error:
            raise HTTPException(
                status_code=400,
                detail=(
                    "The uploaded PDF is "
                    "invalid or unreadable."
                ),
            ) from error

        temporary_path.replace(
            destination_path
        )

        saved_to_destination = True

        clear_sop_cache()

        sop_pages, sop_chunks = (
            load_sop_index()
        )

        document_names = {
            str(page["document"])
            for page in sop_pages
        }

        return {
            "status": "uploaded",
            "filename": safe_filename,
            "uploaded_bytes": uploaded_size,
            "documents": len(
                document_names
            ),
            "pages": len(sop_pages),
            "chunks": len(sop_chunks),
        }

    except HTTPException:
        if saved_to_destination:
            destination_path.unlink(
                missing_ok=True
            )

            clear_sop_cache()

        raise

    except Exception as error:
        if saved_to_destination:
            destination_path.unlink(
                missing_ok=True
            )

            clear_sop_cache()

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to upload and index "
                f"the SOP document: {error}"
            ),
        ) from error

    finally:
        await file.close()

        temporary_path.unlink(
            missing_ok=True
        )

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

        _, sop_chunks = load_sop_index() 
            

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