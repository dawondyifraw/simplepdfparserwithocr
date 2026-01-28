"""Command-line interface for pdfparser."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .parser import parse_pdfs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse PDFs and extract text/tables to CSV.")
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
        "--output",
        type=Path,
        default=None,
        help="Output CSV path (default: data-dir/extracted_content.csv)",
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
    parse_pdfs(data_dir=args.data_dir, output_csv=args.output, pdfs_dir=args.pdfs_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
