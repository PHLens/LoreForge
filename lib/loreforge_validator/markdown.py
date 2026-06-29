"""Markdown and frontmatter helpers for LoreForge validation."""

from __future__ import annotations

import re


FOOTNOTE_REF_RE = re.compile(r"(?<!\^)\[\^([^\]]+)\](?!:)")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)$")


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fields: dict[str, str] = {}
    lines = parts[1].splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" not in line:
            i += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            block: list[str] = []
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if re.match(r"^[A-Za-z0-9_-]+:\s", next_line):
                    break
                if (
                    next_line.startswith("- ")
                    or next_line.startswith("  ")
                    or next_line.startswith("\t")
                    or next_line == ""
                ):
                    block.append(next_line)
                    j += 1
                    continue
                break
            if block:
                value = "\n".join(block).rstrip()
                i = j - 1
        fields[key] = value
        i += 1
    return fields


def list_value(value: str) -> set[str]:
    value = value.strip()
    if not value.startswith("[") or not value.endswith("]"):
        if not value:
            return set()
        items: list[str] = []
        lines = value.splitlines()
        if len(lines) > 1 or value.startswith("- "):
            for line in lines:
                item = line.strip()
                if not item:
                    continue
                if item.startswith("- "):
                    item = item[2:].strip()
                items.extend(part.strip().strip("\"'") for part in item.split(",") if part.strip())
            return {item for item in items if item}
        return {item.strip().strip("\"'") for item in value.split(",") if item.strip()}
    inner = value[1:-1].strip()
    if not inner:
        return set()
    return {item.strip().strip("\"'") for item in inner.split(",") if item.strip()}


def taxonomy(schema_text: str) -> set[str]:
    tags: set[str] = set()
    in_taxonomy = False
    for line in schema_text.splitlines():
        if line.startswith("## "):
            in_taxonomy = line.strip().lower() == "## tag taxonomy"
            continue
        if not in_taxonomy or not line.startswith("- "):
            continue
        value = line[2:].strip()
        if ":" in value:
            value = value.split(":", 1)[1]
        for item in re.split(r"[, ]+", value):
            item = item.strip().strip("`")
            if item:
                tags.add(item)
    return tags


def wikilinks(text: str) -> list[str]:
    return [
        match.split("|", 1)[0].split("#", 1)[0].strip()
        for match in re.findall(r"\[\[([^\]]+)\]\]", text)
    ]


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text
    return f"---{parts[1]}---", parts[2]


def footnote_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    blocks: list[tuple[str, int, int]] = []
    i = 0
    while i < len(lines):
        match = FOOTNOTE_DEF_RE.match(lines[i])
        if not match:
            i += 1
            continue
        label = match.group(1)
        start = i
        i += 1
        while i < len(lines):
            line = lines[i]
            if line.startswith("    ") or line.startswith("\t"):
                i += 1
                continue
            if line.strip() == "":
                next_index = i + 1
                if next_index < len(lines) and (
                    lines[next_index].startswith("    ") or lines[next_index].startswith("\t")
                ):
                    i += 1
                    continue
            break
        blocks.append((label, start, i))
    return blocks


def footnote_labels(body: str) -> tuple[set[str], set[str]]:
    lines = body.splitlines()
    blocks = footnote_blocks(lines)
    defined = {label for label, _, _ in blocks}
    if not blocks:
        refs = set(FOOTNOTE_REF_RE.findall(body))
        return refs, defined

    block_starts = {start: end for _, start, end in blocks}
    filtered: list[str] = []
    i = 0
    while i < len(lines):
        if i in block_starts:
            i = block_starts[i]
            continue
        filtered.append(lines[i])
        i += 1
    refs = set(FOOTNOTE_REF_RE.findall("\n".join(filtered)))
    return refs, defined


def remove_orphan_footnote_definitions(text: str) -> str:
    prefix, body = split_frontmatter(text)
    if not body:
        return text

    lines = body.splitlines()
    blocks = footnote_blocks(lines)
    if not blocks:
        return text

    refs, _ = footnote_labels(body)
    keep_labels = refs
    block_starts = {start: (label, end) for label, start, end in blocks}

    filtered: list[str] = []
    i = 0
    changed = False
    while i < len(lines):
        block = block_starts.get(i)
        if block is not None:
            label, end = block
            if label in keep_labels:
                filtered.extend(lines[i:end])
            else:
                changed = True
            i = end
            continue
        filtered.append(lines[i])
        i += 1

    if not changed:
        return text

    cleaned_body = "\n".join(filtered).rstrip()
    if cleaned_body:
        cleaned_body += "\n"
    return prefix + cleaned_body


def clean_scalar(value: str) -> str:
    return value.strip().strip("\"'")


def heading_exists(text: str, heading: str) -> bool:
    return re.search(rf"^{re.escape(heading)}\s*$", text, flags=re.MULTILINE) is not None
