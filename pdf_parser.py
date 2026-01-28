"""Backward-compatible entry point for the PDF parser."""

from pdfparser.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
