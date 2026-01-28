# PDFParser

Simple PDF parser that extracts text and tables to a CSV, with OCR fallback.

## Install

```bash
pip install -e .
```

## Usage

```bash
pdfparser --data-dir ./data
```

Fetch PDFs from another folder and copy them into your `data/pdfs`:

```bash
pdfparser --source-dir /path/to/pdfs --data-dir ./data --copy-pdfs
```

Output is written to `data/extracted_content.csv` by default.

If a page has no text, OCR is used. You can also save OCR images:

```bash
pdfparser --data-dir ./data --save-ocr-images
```

## Data layout

```
PDFParser/
  data/
    pdfs/
      your-files.pdf
```

## Programmatic

```python
from pdfparser import parse_pdfs

parse_pdfs(data_dir="./data")
```

## Dependencies

- `pdfplumber`
- `pdf2image`
- `pytesseract`
- `pandas`

## Output columns

The CSV includes file metadata (size, modified time, total pages) plus per-page OCR info.

## License

MIT
