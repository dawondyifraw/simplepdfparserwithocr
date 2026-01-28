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

Output is written to `data/extracted_content.csv` by default.

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

## License

MIT
