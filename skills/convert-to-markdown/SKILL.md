---
name: convert-to-markdown
description: Convert documents to Markdown format. Supports Confluence MIME exports (.doc), Word documents (.docx), HTML files, and plain text. Use when converting documents, wiki exports, or when user mentions "convert to markdown", "doc to md", "html to markdown", "转markdown", "文档转换".
---

# Convert to Markdown

Universal document to Markdown converter.

## Environment Setup

The runtime entrypoint is `scripts/convert_to_markdown.py`. All commands below assume you start from the skill root and then enter `scripts/`.

Recommended bootstrap on a fresh machine:

```bash
cd scripts
uv sync
```

If `uv` is not on `PATH` but `scripts/.venv` already exists, reuse the local environment directly:

```bash
cd scripts
./.venv/bin/python convert_to_markdown.py --help
```

If you prefer activating the environment first:

```bash
cd scripts
source .venv/bin/activate
python convert_to_markdown.py --help
```

Operational rule:

- Prefer `uv sync` to create or refresh the environment.
- Prefer `./.venv/bin/python convert_to_markdown.py ...` when `uv` is unavailable in the current shell.
- For old `.doc` format (pre-2007 Word), system package `antiword` is required: `sudo apt install antiword`

## Supported formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Confluence MIME export | `.doc` | Wiki exports containing HTML + images |
| Word document | `.docx` | Via `mammoth` library |
| HTML | `.html`, `.htm` | Direct HTML to Markdown |
| Plain text | `.txt` | Clean up formatting |
| Old Word format | `.doc` | Requires `antiword` (system package) |

## Quick Start

Install dependencies once:

```bash
cd scripts && uv sync
```

Convert all supported files in current directory:

```bash
cd scripts && ./.venv/bin/python convert_to_markdown.py
```

Convert a specific file:

```bash
cd scripts && ./.venv/bin/python convert_to_markdown.py /path/to/file.docx
```

Convert to specific output directory:

```bash
cd scripts && ./.venv/bin/python convert_to_markdown.py /path/to/file.html /path/to/output/
```

## Workflow

1. **Detect file type**: The script auto-detects format by content, not extension
2. **Run conversion**: Specify file or let it batch-convert current directory
3. **Check output**:
   - Markdown: `文件名.md` in same directory or specified output directory
   - Images (if extracted): `images/` subdirectory

## Format-specific notes

### Confluence MIME exports
- Exported via Confluence "Export to Word" feature
- Actually MIME format (not real Word)
- Images extracted to `images/` folder
- No external dependencies needed (stdlib only)

### Word documents (.docx)
- Converted via `mammoth` library (installed with `uv sync`)
- Best results with simple formatting
- Tables and lists supported

### Old Word format (.doc)
- Requires system tool `antiword`:
  ```bash
  # Ubuntu/Debian
  sudo apt install antiword

  # CentOS/RHEL
  sudo yum install antiword

  # macOS
  brew install antiword
  ```
- Limited formatting support

### HTML files
- Direct conversion, no dependencies
- Preserves headers, lists, tables, links

## Output structure

```
output/
├── 文件名.md          # Converted Markdown
└── images/            # Extracted images (if any)
    ├── image1.png
    └── image2.jpg
```

## Examples

**Example 1: Batch convert**
```bash
cd /path/to/documents
/path/to/skill/scripts/.venv/bin/python /path/to/skill/scripts/convert_to_markdown.py
```

**Example 2: Single file**
```bash
cd scripts && ./.venv/bin/python convert_to_markdown.py report.docx
```

**Example 3: With output directory**
```bash
cd scripts && ./.venv/bin/python convert_to_markdown.py page.html /path/to/output/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `mammoth not installed` | Run `uv sync` in scripts directory |
| `old .doc format` | Install antiword: `sudo apt install antiword` |
| `unknown file type` | Check with `file` command |
| Images not extracted | Verify file is Confluence MIME format |
| Empty output | Verify file has content |

## Dependencies

### Python version

- **Required**: Python 3.8+
- Managed via `uv sync` in scripts directory

### Standard library (always available)

- `email` - MIME parsing for Confluence exports
- `html.parser` - HTML to Markdown conversion
- `pathlib` - Path handling
- `re` - Regex for text cleanup
- `sys` - Command line arguments

### Installed via pyproject.toml

- `mammoth` - Word .docx conversion

### System packages (optional)

- `antiword` - For old .doc format (not installable via pip)