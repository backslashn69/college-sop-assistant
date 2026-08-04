import re
from pathlib import Path

from pypdf import PdfReader


SOP_DIRECTORY = Path(__file__).parent / "data" / "sops"

STEP_HEADING_PATTERN = re.compile(
    r"^Step\s+\d+\s*:\s*.+$",
    re.IGNORECASE,
)

MAIN_HEADING_PATTERN = re.compile(
    r"^\d+\.\s+[A-Z][A-Za-z0-9/&(),'\-\s]{2,70}$"
)

BULLET_PATTERN = re.compile(
    r"^[•●▪◦]\s*"
)

SUB_BULLET_PATTERN = re.compile(
    r"^[o○]\s+"
)

STANDALONE_ARROW_PATTERN = re.compile(
    r"^[↓→]+$"
)


def clean_pdf_line(raw_line: str) -> str:
    line = raw_line.replace("\u00ad", "").strip()

    if not line:
        return ""

    if STANDALONE_ARROW_PATTERN.fullmatch(line):
        return ""

    line = re.sub(
        r"\s+",
        " ",
        line,
    )

    if BULLET_PATTERN.match(line):
        line = BULLET_PATTERN.sub(
            "- ",
            line,
        )

    elif SUB_BULLET_PATTERN.match(line):
        line = SUB_BULLET_PATTERN.sub(
            "- ",
            line,
        )

    return line.strip()


def load_all_sops() -> list[dict[str, str | int]]:
    if not SOP_DIRECTORY.exists():
        raise FileNotFoundError(
            f"SOP directory was not found at: {SOP_DIRECTORY}"
        )

    pdf_files = sorted(
        SOP_DIRECTORY.glob("*.pdf")
    )

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF documents were found in: {SOP_DIRECTORY}"
        )

    extracted_pages: list[dict[str, str | int]] = []

    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            raw_text = page.extract_text()

            if not raw_text or not raw_text.strip():
                continue

            cleaned_lines = [
                clean_pdf_line(line)
                for line in raw_text.splitlines()
            ]

            cleaned_lines = [
                line
                for line in cleaned_lines
                if line
            ]

            if not cleaned_lines:
                continue

            extracted_pages.append(
                {
                    "document": pdf_file.name,
                    "page": page_number,
                    "text": "\n".join(cleaned_lines),
                }
            )

    if not extracted_pages:
        raise ValueError(
            "The SOP files were found, but no readable text was extracted."
        )

    return extracted_pages


def is_section_heading(line: str) -> bool:
    if STEP_HEADING_PATTERN.fullmatch(line):
        return True

    if MAIN_HEADING_PATTERN.fullmatch(line):
        return not line.endswith(
            (
                ".",
                ":",
                ";",
                "?",
                "!",
            )
        )

    return line == "Document Control"


def get_section_type(title: str) -> str:
    lowered_title = title.lower()

    if lowered_title.startswith("step "):
        return "procedure"

    if "quick reference" in lowered_title:
        return "reference"

    if "common issues" in lowered_title:
        return "troubleshooting"

    if "policies" in lowered_title:
        return "policy"

    return "section"


def build_sop_chunks(
    sop_pages: list[dict[str, str | int]],
) -> list[dict[str, str | int]]:
    chunks: list[dict[str, str | int]] = []

    current_document: str | None = None
    current_title = "Document Overview"
    current_type = "section"
    current_page_start = 1
    current_page_end = 1
    current_lines: list[str] = []

    def save_current_section() -> None:
        nonlocal current_lines

        section_text = "\n".join(
            current_lines
        ).strip()

        if current_document is None or not section_text:
            current_lines = []
            return

        chunks.append(
            {
                "document": current_document,
                "title": current_title,
                "type": current_type,
                "page": current_page_start,
                "page_start": current_page_start,
                "page_end": current_page_end,
                "text": section_text,
            }
        )

        current_lines = []

    for page in sop_pages:
        document = str(page["document"])
        page_number = int(page["page"])
        page_lines = str(page["text"]).splitlines()

        if current_document != document:
            save_current_section()

            current_document = document
            current_title = "Document Overview"
            current_type = "section"
            current_page_start = page_number
            current_page_end = page_number

        for line in page_lines:
            cleaned_line = line.strip()

            if not cleaned_line:
                continue

            if is_section_heading(cleaned_line):
                save_current_section()

                current_title = cleaned_line
                current_type = get_section_type(
                    cleaned_line
                )
                current_page_start = page_number
                current_page_end = page_number
                continue

            current_page_end = page_number
            current_lines.append(cleaned_line)

    save_current_section()

    if not chunks:
        raise ValueError(
            "The SOP documents were loaded, but no sections were created."
        )

    return chunks