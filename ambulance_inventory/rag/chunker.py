"""Chunking utilities for catalog text."""

from typing import Iterable, List


_NOISE_KEYWORDS = (
    "www.",
    "http://",
    "https://",
    "電話",
    "TEL",
    "FAX",
    "地址",
    "E-mail",
    "Email",
    "Copyright",
    "版權",
)

_HEADING_KEYWORDS = (
    "型號",
    "Model",
    "規格",
    "特色",
    "功能",
    "尺寸",
    "重量",
    "材質",
    "配件",
    "承重",
    "載重",
)


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    if not text:
        return []

    paragraphs = _clean_lines(text.split("\n"))
    return _pack_chunks(paragraphs, max_chars=max_chars, overlap=overlap)


def chunk_catalog_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    if not text:
        return []

    lines = _clean_lines(text.split("\n"))
    spec_chunks, remaining = _extract_spec_blocks(lines)
    sections = _split_sections(remaining)
    chunks: List[str] = []

    chunks.extend(spec_chunks)
    for section in sections:
        chunks.extend(_pack_chunks(section, max_chars=max_chars, overlap=overlap))

    return chunks


def _clean_lines(lines: Iterable[str]) -> List[str]:
    cleaned: List[str] = []
    for line in lines:
        line = _normalize_units(line.strip())
        if not line:
            continue
        if any(key in line for key in _NOISE_KEYWORDS):
            continue
        cleaned.append(line)
    return cleaned


def _normalize_units(text: str) -> str:
    return (
        text.replace("㎏", "kg")
        .replace("ＫＧ", "kg")
        .replace("ｋｇ", "kg")
        .replace("公分", "cm")
        .replace("公厘", "mm")
    )


def _split_sections(lines: List[str]) -> List[List[str]]:
    sections: List[List[str]] = []
    current: List[str] = []
    last_heading = ""

    for line in lines:
        if _is_heading(line):
            if current:
                sections.append(current)
                current = []
            last_heading = line
            current.append(line)
            continue

        if _looks_like_model_line(line) and current:
            sections.append(current)
            current = []
            if last_heading:
                current.append(last_heading)

        current.append(line)

    if current:
        sections.append(current)

    return sections


def _extract_spec_blocks(lines: List[str]) -> tuple[List[str], List[str]]:
    spec_chunks: List[str] = []
    remaining: List[str] = []
    model_title = ""
    skip_indices = set()

    for idx, line in enumerate(lines):
        if _looks_like_model_line(line):
            model_title = line

        if "SPECIFICATIONS" in line.upper():
            block = [line]
            j = idx + 1
            while j < len(lines):
                next_line = lines[j]
                if _is_heading(next_line) or next_line.upper().startswith("MODEL "):
                    break
                if "PATIENT HANDLING" in next_line.upper():
                    break
                block.append(next_line)
                j += 1

            for k in range(idx, j):
                skip_indices.add(k)

            if model_title:
                block.insert(0, model_title)
            spec_chunks.append("\n".join(block))

    for idx, line in enumerate(lines):
        if idx in skip_indices:
            continue
        remaining.append(line)

    return spec_chunks, remaining


def _is_heading(line: str) -> bool:
    if len(line) <= 40 and any(key in line for key in _HEADING_KEYWORDS):
        return True
    if line.isupper() and len(line) <= 60:
        return True
    return False


def _looks_like_model_line(line: str) -> bool:
    if "Model" in line or "型號" in line:
        return True
    if any(ch.isdigit() for ch in line) and "-" in line and len(line) <= 60:
        return True
    return False


def _pack_chunks(lines: List[str], max_chars: int, overlap: int) -> List[str]:
    chunks: List[str] = []
    current = ""

    for line in lines:
        if not current:
            current = line
            continue

        if len(current) + 1 + len(line) <= max_chars:
            current = f"{current}\n{line}"
            continue

        chunks.append(current)
        if overlap > 0:
            tail = current[-overlap:]
            current = f"{tail}\n{line}"
        else:
            current = line

    if current:
        chunks.append(current)

    return chunks
