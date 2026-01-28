"""Command-line interface for pdfparser."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .parser import parse_pdfs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse PDFs and extract text/tables to CSV.")
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=None,
        help="Source folder to fetch PDFs from",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Base data directory containing a 'pdfs' folder (default: package data dir)",
    )
    parser.add_argument(
        "--pdfs-dir",
        type=Path,
        default=None,
        help="Override PDFs directory (default: data-dir/pdfs)",
    )
    parser.add_argument(
        "--copy-pdfs",
        action="store_true",
        help="Copy PDFs from source-dir into pdfs-dir before processing",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output CSV path (default: data-dir/extracted_content.csv)",
    )
    parser.add_argument(
        "--save-ocr-images",
        action="store_true",
        help="Save OCR images when text extraction fails",
    )
    parser.add_argument(
        "--ocr-images-dir",
        type=Path,
        default=None,
        help="Directory to save OCR images (default: data-dir/ocr_images)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (default: INFO)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    parse_pdfs(
        data_dir=args.data_dir,
        output_csv=args.output,
        pdfs_dir=args.pdfs_dir,
        source_dir=args.source_dir,
        copy_pdfs=args.copy_pdfs,
        save_ocr_images=args.save_ocr_images,
        ocr_images_dir=args.ocr_images_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
