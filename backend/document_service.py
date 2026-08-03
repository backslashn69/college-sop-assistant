from pathlib import Path

from pypdf import PdfReader


SOP_DIRECTORY = Path(__file__).parent / "data" / "sops"


def load_all_sops() -> list[dict[str, str | int]]:
    if not SOP_DIRECTORY.exists():
        raise FileNotFoundError(
            f"SOP directory was not found at: {SOP_DIRECTORY}"
        )

    pdf_files = list(SOP_DIRECTORY.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF documents were found in: {SOP_DIRECTORY}"
        )

    extracted_pages: list[dict[str, str | int]] = []

    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()

            if not page_text or not page_text.strip():
                continue

            extracted_pages.append(
                {
                    "document": pdf_file.name,
                    "page": page_number,
                    "text": page_text.strip(),
                }
            )

    if not extracted_pages:
        raise ValueError(
            "The SOP files were found, but no readable text was extracted."
        )

    return extracted_pages