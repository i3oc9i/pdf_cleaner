# Copilot Instructions for pdf_cleaner

## Project Overview

Single-file CLI tool using PyMuPDF to sanitize PDFs by physically removing links and redacting text. The tool operates on two PDF layers simultaneously and ensures permanent data removal through garbage collection.

## Architecture

**Core Design**: [pdf_cleaner.py](../pdf_cleaner.py) contains all logic in two functions:

- `process_pdf()`: Dual-layer scrubbing engine (links + text)
- `main()`: CLI with argparse

**Dual-Layer Operation**:

1. **Link Layer**: Delete link annotations (`.delete_link()`) + redact entire clickable text area (`add_redact_annot()`)
2. **Text Layer**: Search standalone text (`.search_for()`) + redact non-link matches
3. Critical: Call `.apply_redactions()` after adding annotations to physically remove data

**Data Permanence**: Output uses `doc.save(..., garbage=3, deflate=True)` to permanently purge scrubbed content and prevent recovery.

## Development Workflow

```bash
# Setup (uses uv for fast dependency management)
uv pip install -e .              # Install in dev mode
uv pip install -e ".[dev]"       # With task runner (poethepoet)

# Running
pdf_cleaner file.pdf "pattern"                    # Basic scrub
pdf_cleaner file.pdf "pattern" -r "[REDACTED]"   # With replacement
pdf_cleaner file.pdf "pattern" --dry-run         # Preview only

# Cleanup
poe clean  # Removes dist/, __pycache__/, *.egg-info/ (preserves .venv/, uv.lock)
```

## Key Patterns

**Shebang**: File uses `#!/usr/bin/env -S uv run` for direct execution with uv

**Rect Intersection Logic**: When processing text, skip instances already covered by link redactions using `rect.intersects(inst)` to avoid double-processing

**Error Handling**: Single try-catch wraps all processing; errors call `sys.exit(1)`

**Output Naming**: Consistently use `{base}_clean{ext}` pattern (not `_copy` as README mentions)

## Project Conventions

- Python 3.12+ required (specified in [pyproject.toml](../pyproject.toml))
- Single-file architecture: All logic stays in `pdf_cleaner.py`
- No external config files or database
- Output always preserves original file
- Case-insensitive pattern matching (`target_string.lower()`)
- Dry-run mode must count but not execute removals

## Dependencies

- **PyMuPDF (fitz)**: Core PDF manipulation (≥1.26.7)
- **uv**: Fast package manager (not in dependencies but used for development)
- **poethepoet**: Optional task runner for cleanup scripts

## Testing Approach

When adding features:

1. Test with `--dry-run` first to verify detection logic
2. Verify output with PDF viewer that shows links (not all viewers render them)
3. Check garbage collection: Use `pdfinfo` or reopen PDF to confirm no trace of redacted content
4. Test edge cases: Empty replacements, overlapping text/links, multi-page documents

## Common Pitfalls

- Don't modify in-place; always create `_clean` output file
- Remember `page.apply_redactions()` is required after adding redaction annotations
- Link rectangles cover entire clickable area, not just matching substring
- Ensure `garbage=3` on save to prevent data recovery
