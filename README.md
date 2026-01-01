# PDF Link & Text Scrub

A powerful, lightweight CLI tool built with Python and **PyMuPDF** to sanitize PDF documents. This tool doesn't just make links unclickable; it physically scrubs the associated text from the document and can replace it with a label of your choice.

## ✨ Features

* **Dual-Layer Scrubbing:** Removes both the interactive link (annotation layer) and the actual text (content stream).
* **Fuzzy Matching:** Target links and text using partial strings (e.g., searching `internal` catches `internal-server.com`).
* **Text Replacement:** Replace sensitive data with custom strings like `[REDACTED]` or `[HIDDEN]`.
* **Dry Run Mode:** Audit your document to see exactly what would be removed without creating a new file.
* **Safe Output:** Always preserves your original file by saving results to `{filename}_copy.pdf`.
* **Optimized Output:** Automatically compresses and "garbage collects" the PDF to ensure the scrubbed data is permanently unrecoverable.

---

## 🚀 Installation

This project uses `uv` for high-performance dependency management.

1. **Install `uv**` (if not already installed):
* **macOS/Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`
* **Windows:** `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`


2. **Clone and install:**
```bash
git clone <repository-url>
cd pdf_cleaner
uv pip install -e .
```

3. **For development** (includes task runner):
```bash
uv pip install -e ".[dev]"
```

---

## 🧹 Development

Clean build artifacts:
```bash
poe clean
```

This removes `dist/`, `__pycache__/`, and `*.egg-info/` while preserving `.venv/` and `uv.lock`.

---

## 🛠 Usage

The tool requires two main arguments: the **PDF file** and the **pattern** (text or URL part) you want to remove.

### 1. Basic Scrub

Removes the link and its associated text, saves to `file_clean.pdf`:

```bash
pdf_cleaner report.pdf "confidential.com"
```

### 2. Scrub and Replace

Removes the target and inserts a custom placeholder in its place:

```bash
pdf_cleaner report.pdf "secret-link.com" --replace "[REDACTED]"
```

### 3. Dry Run (Auditing)

List all matches found without creating an output file:

```bash
pdf_cleaner report.pdf "internal-site" --dry-run
```

---

## 📖 How it Works

Understanding the difference between the two layers the tool cleans is essential:

1. **Link Layer (Annotations):** These are invisible "hotspots" that trigger a browser or email client. The tool deletes these dictionary objects by matching the `uri` key and redacts the entire clickable text area (not just the matching word).
2. **Text Layer (Content Stream):** For standalone text matches (not part of links), the tool uses **Redaction Annotations** to identify the coordinates, paint over them (white fill), and then physically remove the character bytes from the PDF structure.
3. **Purging:** Upon saving, the tool uses `garbage=3`. This is a high-level cleanup that removes unreferenced objects, ensuring that a savvy user cannot "undo" the redaction to see the original text.

---

## 📋 Arguments

| Argument | Short | Description |
| --- | --- | --- |
| `file` | N/A | **Required.** The path to the source PDF file. |
| `pattern` | N/A | **Required.** The string to search for in both links and text. |
| `--replace` | `-r` | Optional. The text to display where the old text was removed. |
| `--dry-run` | N/A | Optional. Lists matches on the console without generating a file. |

---

