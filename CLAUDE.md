# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF Link & Text Scrub - A CLI tool using PyMuPDF to sanitize PDF documents by removing links and redacting text.

## Commands

```bash
# Install
uv pip install -e .

# Run the tool
pdf_cleaner <file.pdf> "<pattern>" [--replace "<text>"] [--dry-run]

# Examples
pdf_cleaner report.pdf "confidential.com"
pdf_cleaner report.pdf "secret-link.com" --replace "[REDACTED]"
pdf_cleaner report.pdf "internal-site" --dry-run
```

## Architecture

Single-file CLI tool (`pdf_cleaner.py`) with two main functions:
- `process_pdf()`: Core logic that handles both link removal (annotation layer) and text redaction (content stream)
- `main()`: CLI argument parsing with argparse

The tool operates on two PDF layers:
1. **Link Layer**: Removes clickable link annotations by matching URIs and redacts the entire associated text area
2. **Text Layer**: For standalone text matches, uses PyMuPDF redaction annotations to physically remove and optionally replace text

Output files are saved as `{filename}_clean.pdf` with `garbage=3` compression to permanently remove scrubbed data.
