"""Core parsing logic for PDFs."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
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
    source_dir: Optional[Path] = None,
    copy_pdfs: bool = False,
    save_ocr_images: bool = False,
    ocr_images_dir: Optional[Path] = None,
    logger: Optional[logging.Logger] = None,
) -> Path:
    """Parse PDFs under a data directory and write a CSV of extracted content.

    Args:
        data_dir: Base data directory containing a `pdfs/` folder.
        output_csv: Path to write CSV output (defaults to data_dir/extracted_content.csv).
        pdfs_dir: Explicit PDFs directory (defaults to data_dir/pdfs).
        source_dir: Optional source directory to fetch PDFs from.
        copy_pdfs: If True and source_dir is provided, copy PDFs into pdfs_dir.
        save_ocr_images: If True, save OCR images to ocr_images_dir.
        ocr_images_dir: Directory for OCR images (defaults to data_dir/ocr_images).
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

    if source_dir is not None:
        source_dir = Path(source_dir)
        if copy_pdfs:
            pdfs_dir.mkdir(parents=True, exist_ok=True)
            for src in _iter_pdf_paths(source_dir):
                shutil.copy2(src, pdfs_dir / src.name)
        else:
            pdfs_dir = source_dir

    if output_csv is None:
        output_csv = data_dir / "extracted_content.csv"
    else:
        output_csv = Path(output_csv)

    if ocr_images_dir is None:
        ocr_images_dir = data_dir / "ocr_images"
    else:
        ocr_images_dir = Path(ocr_images_dir)

    log = logger or logging.getLogger("pdfparser")

    rows = []

    for pdf_path in _iter_pdf_paths(pdfs_dir):
        log.info("Processing PDF: %s", pdf_path)
        ocr_pages = None
        stat = pdf_path.stat()
        file_meta = {
            "file": pdf_path.name,
            "file_size_bytes": stat.st_size,
            "file_modified_utc": datetime.utcfromtimestamp(stat.st_mtime).isoformat() + "Z",
        }

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for page_number, page in enumerate(pdf.pages, 1):
                text = (page.extract_text() or "").strip()
                ocr_used = False
                ocr_image_path = ""

                if not text:
                    if ocr_pages is None:
                        ocr_pages = convert_from_path(str(pdf_path), dpi=300)
                    ocr_used = True
                    ocr_image = ocr_pages[page_number - 1]
                    if save_ocr_images:
                        ocr_images_dir.mkdir(parents=True, exist_ok=True)
                        ocr_image_path = str(
                            ocr_images_dir / f"{pdf_path.stem}_page_{page_number}.png"
                        )
                        ocr_image.save(ocr_image_path, format="PNG")
                    text = pytesseract.image_to_string(ocr_image)

                rows.append(
                    {
                        **file_meta,
                        "total_pages": total_pages,
                        "page": page_number,
                        "type": "text",
                        "content": text,
                        "ocr_used": ocr_used,
                        "ocr_image_path": ocr_image_path,
                    }
                )

                for table in page.extract_tables() or []:
                    rows.append(
                        {
                            **file_meta,
                            "total_pages": total_pages,
                            "page": page_number,
                            "type": "table",
                            "content": table,
                            "ocr_used": ocr_used,
                            "ocr_image_path": ocr_image_path,
                        }
                    )

    df = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    return output_csv
