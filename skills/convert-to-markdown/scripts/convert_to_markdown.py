#!/usr/bin/env python3
"""
Universal document to Markdown converter.

Supports:
- Confluence MIME exports (.doc from Confluence "Export to Word")
- Word documents (.docx via mammoth)
- HTML files
- Plain text files

Usage:
    python convert_to_markdown.py <input_file> [output_dir]
    python convert_to_markdown.py  # Convert all supported files in current directory
"""
import email
import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from html import unescape

try:
    import mammoth
    HAS_MAMMOTH = True
except ImportError:
    HAS_MAMMOTH = False


class HTMLToMarkdown(HTMLParser):
    """Convert HTML to Markdown, skipping style/script content."""

    def __init__(self, image_map=None):
        super().__init__()
        self.result = []
        self.current_tag = None
        self.list_depth = 0
        self.skip_content = False
        self.image_map = image_map or {}
        self.in_pre = False
        self.in_table = False
        self.table_rows = []
        self.in_cell = False
        self.current_cell = ''
        self.current_row = []
        self.link_url = ''

    def handle_starttag(self, tag, attrs):
        attrs_dict = {k: v for k, v in attrs}
        self.current_tag = tag

        if tag in ['style', 'script', 'head', 'meta', 'link', 'noscript']:
            self.skip_content = True
            return

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            self.result.append('\n' + '#' * level + ' ')

        elif tag == 'li':
            self.result.append('\n' + '  ' * self.list_depth + '- ')

        elif tag in ['ul', 'ol']:
            self.list_depth += 1

        elif tag == 'br':
            self.result.append('\n')

        elif tag in ['strong', 'b']:
            self.result.append('**')

        elif tag in ['em', 'i']:
            self.result.append('*')

        elif tag == 'code' and not self.in_pre:
            self.result.append('`')

        elif tag == 'pre':
            self.in_pre = True
            self.result.append('\n```\n')

        elif tag == 'a':
            href = attrs_dict.get('href', '')
            if href:
                self.result.append('[')
                self.link_url = unescape(href)

        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', '')
            if src in self.image_map:
                src = self.image_map[src]
            src = unescape(src)
            self.result.append(f'![{alt}]({src})')

        elif tag == 'table':
            self.in_table = True
            self.table_rows = []
            self.result.append('\n')

        elif tag == 'tr':
            self.current_row = []

        elif tag in ['td', 'th']:
            self.in_cell = True
            self.current_cell = ''

    def handle_endtag(self, tag):
        if tag in ['style', 'script', 'head', 'meta', 'link', 'noscript']:
            self.skip_content = False
            return

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.result.append('\n')

        elif tag in ['ul', 'ol']:
            self.list_depth -= 1
            if self.list_depth == 0:
                self.result.append('\n')

        elif tag == 'p':
            self.result.append('\n\n')

        elif tag in ['strong', 'b']:
            self.result.append('**')

        elif tag in ['em', 'i']:
            self.result.append('*')

        elif tag == 'code' and not self.in_pre:
            self.result.append('`')

        elif tag == 'pre':
            self.in_pre = False
            self.result.append('\n```\n')

        elif tag == 'a':
            self.result.append(f']({self.link_url})')

        elif tag in ['td', 'th']:
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())
            self.current_cell = ''

        elif tag == 'tr':
            if self.current_row:
                self.table_rows.append(self.current_row)
                self.result.append('| ' + ' | '.join(self.current_row) + ' |\n')

        elif tag == 'table':
            self.in_table = False
            if self.table_rows:
                num_cols = len(self.table_rows[0])
                self.result.append('| ' + ' | '.join(['---'] * num_cols) + ' |\n')

        self.current_tag = None

    def handle_data(self, data):
        if self.skip_content:
            return

        if self.in_table and self.in_cell:
            self.current_cell += data
            return

        if not self.in_pre:
            data = re.sub(r'[ \t]+', ' ', data)
            data = re.sub(r'\n+', '\n', data)

        self.result.append(data)

    def get_markdown(self):
        text = ''.join(self.result)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'(?<!\!)\[\]\([^\)]*\)', '', text)
        return text.strip()


def detect_file_type(file_path):
    """Detect the actual file type."""
    path = Path(file_path)

    # Check extension first
    ext = path.suffix.lower()

    if ext == '.docx':
        return 'docx'

    if ext == '.html' or ext == '.htm':
        return 'html'

    if ext == '.md':
        return 'markdown'  # Already markdown

    if ext == '.txt':
        return 'text'

    if ext == '.doc':
        # Could be Confluence MIME or old Word format
        # Check file content
        with open(path, 'rb') as f:
            header = f.read(100)

        # MIME format starts with "Date:" or "Message-ID:"
        if header.startswith(b'Date:') or b'MIME-Version' in header:
            return 'confluence_mime'

        # Old .doc format (OLE) starts with D0 CF 11 E0
        if header[:4] == b'\xd0\xcf\x11\xe0':
            return 'doc_old'

        # Might be plain text misnamed as .doc
        try:
            content = header.decode('utf-8')
            if content.isprintable() or '\n' in content:
                return 'text'
        except:
            pass

    return 'unknown'


def extract_confluence_mime(file_path, output_dir):
    """Extract HTML and images from Confluence MIME export."""
    with open(file_path, 'rb') as f:
        msg = email.message_from_binary_file(f)

    html_content = None
    image_map = {}

    images_dir = output_dir / 'images'
    images_dir.mkdir(exist_ok=True)

    for part in msg.walk():
        content_type = part.get_content_type()

        if content_type == 'text/html':
            payload = part.get_payload(decode=True)
            html_content = payload.decode('utf-8')

        elif content_type == 'application/octet-stream' or content_type.startswith('image/'):
            content_location = part.get('Content-Location', '')
            if content_location:
                filename = Path(content_location).name
            else:
                continue

            payload = part.get_payload(decode=True)
            if not payload:
                continue

            # Detect image type from magic bytes
            if payload[:8] == b'\x89PNG\r\n\x1a\n':
                ext = 'png'
            elif payload[:2] == b'\xff\xd8':
                ext = 'jpg'
            elif payload[:6] in (b'GIF87a', b'GIF89a'):
                ext = 'gif'
            else:
                ext = 'png'

            if not filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                filename = f"{filename}.{ext}"

            image_path = images_dir / filename
            with open(image_path, 'wb') as img_file:
                img_file.write(payload)

            base_name = filename.rsplit('.', 1)[0]
            image_map[base_name] = f"images/{filename}"
            image_map[filename] = f"images/{filename}"

    return html_content, image_map


def convert_docx(file_path, output_dir):
    """Convert .docx to Markdown using mammoth."""
    if not HAS_MAMMOTH:
        print("  Error: mammoth not installed. Run: pip install mammoth")
        return None

    with open(file_path, 'rb') as f:
        result = mammoth.convert_to_html(f)
        html = result.value

    markdown = html_to_markdown(html)

    # Print warnings
    for msg in result.messages:
        print(f"  Warning: {msg}")

    return markdown


def convert_html(file_path, output_dir):
    """Convert HTML file to Markdown."""
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    return html_to_markdown(html)


def convert_text(file_path, output_dir):
    """Convert plain text to Markdown (just clean up formatting)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert CRLF to LF
    text = text.replace('\r\n', '\n')

    return text.strip()


def html_to_markdown(html, image_map=None):
    """Convert HTML string to Markdown."""
    parser = HTMLToMarkdown(image_map)
    parser.feed(html)
    return parser.get_markdown()


def convert_file(input_path, output_dir=None):
    """Convert a single file to Markdown."""
    input_path = Path(input_path)

    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / (input_path.stem + '.md')

    print(f"Converting: {input_path.name}")

    file_type = detect_file_type(input_path)
    print(f"  Type: {file_type}")

    try:
        markdown = None
        image_map = {}

        if file_type == 'confluence_mime':
            html, image_map = extract_confluence_mime(input_path, output_dir)
            if html:
                markdown = html_to_markdown(html, image_map)

        elif file_type == 'docx':
            markdown = convert_docx(input_path, output_dir)

        elif file_type == 'html':
            markdown = convert_html(input_path, output_dir)

        elif file_type == 'text':
            markdown = convert_text(input_path, output_dir)

        elif file_type == 'markdown':
            print("  Skipping: already Markdown")
            return None

        elif file_type == 'doc_old':
            print("  Error: old .doc format requires antiword or LibreOffice")
            print("  Install: sudo apt install antiword")
            return None

        else:
            print("  Error: unknown file type")
            return None

        if markdown:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)

            print(f"  Output: {output_path.name} ({len(markdown)} chars)")
            if image_map:
                print(f"  Images: {len(image_map)} extracted")
            return output_path

    except Exception as e:
        print(f"  Error: {e}")
        return None


def print_help():
    """Print command usage."""
    print("""Universal document to Markdown converter.

Usage:
  python convert_to_markdown.py
  python convert_to_markdown.py <input_file>
  python convert_to_markdown.py <input_file> <output_dir>

Supported formats:
  .doc   Confluence MIME export, or old Word with antiword installed
  .docx  Word document via mammoth
  .html  HTML file
  .htm   HTML file
  .txt   Plain text

With no arguments, converts all supported files in the current directory.""")


def main():
    """Convert files to Markdown."""
    args = sys.argv[1:]

    if any(arg in ('-h', '--help') for arg in args):
        print_help()
        return

    if len(args) == 1:
        convert_file(args[0])
    elif len(args) == 2:
        convert_file(args[0], args[1])
    elif len(args) > 2:
        for input_file in args:
            convert_file(input_file)
    else:
        # Convert all supported files in current directory
        current_dir = Path.cwd()

        supported_exts = ['.doc', '.docx', '.html', '.htm', '.txt']
        files = []
        for ext in supported_exts:
            files.extend(current_dir.glob(f'*{ext}'))

        if not files:
            print(f"No supported files found in {current_dir}")
            print("Supported formats: .doc (Confluence MIME), .docx, .html, .txt")
            return

        print(f"Found {len(files)} files in {current_dir}")

        for f in files:
            convert_file(f)


if __name__ == "__main__":
    main()
