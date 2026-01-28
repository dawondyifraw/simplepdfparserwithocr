"""Core parsing logic for PDFs."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Optional

import pdfplumber
import pandas as pd
from pdf2image import convert_from_path
import pytesseract


def _iter_pdf_paths(pdfs_dir: Path) -> Iterable[Path]:
    return sorted(pdfs_dir.glob("*.pdf"))


def parse_pdfs(
    data_dir: Optional[Path] = None,
    output_csv: Optional[Path] = None,
    pdfs_dir: Optional[Path] = None,
    logger: Optional[logging.Logger] = None,
) -> Path:
    """Parse PDFs under a data directory and write a CSV of extracted content.

    Args:
        data_dir: Base data directory containing a `pdfs/` folder.
        output_csv: Path to write CSV output (defaults to data_dir/extracted_content.csv).
        pdfs_dir: Explicit PDFs directory (defaults to data_dir/pdfs).
        logger: Optional logger for progress messages.

    Returns:
        Path to the CSV file written.
    """
    if data_dir is None:
        data_dir = Path(__file__).parent.parent / "data"
    else:
        data_dir = Path(data_dir)

    if pdfs_dir is None:
        pdfs_dir = data_dir / "pdfs"
    else:
        pdfs_dir = Path(pdfs_dir)

    if output_csv is None:
        output_csv = data_dir / "extracted_content.csv"
    else:
        output_csv = Path(output_csv)

    log = logger or logging.getLogger("pdfparser")

    rows = []

    for pdf_path in _iter_pdf_paths(pdfs_dir):
        log.info("Processing PDF: %s", pdf_path)
        ocr_pages = None

        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, 1):
                text = (page.extract_text() or "").strip()

                if not text:
                    if ocr_pages is None:
                        ocr_pages = convert_from_path(str(pdf_path), dpi=300)
                    text = pytesseract.image_to_string(ocr_pages[page_number - 1])

                rows.append(
                    {
                        "file": pdf_path.name,
                        "page": page_number,
                        "type": "text",
                        "content": text,
                    }
                )

                for table in page.extract_tables() or []:
                    rows.append(
                        {
                            "file": pdf_path.name,
                            "page": page_number,
                            "type": "table",
                            "content": table,
                        }
                    )

    df = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    return output_csv
