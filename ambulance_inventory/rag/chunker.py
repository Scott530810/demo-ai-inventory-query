"""
型錄文件切分模組
針對醫療設備型錄的特殊處理：去雜訊、單位正規化、規格表聚合
"""

from typing import List, Tuple
import re


# 雜訊關鍵字（需要過濾的內容）
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
    "頁次",
    "Page",
)

# 標題關鍵字
_HEADING_KEYWORDS = (
    "型號",
    "Model",
    "規格",
    "SPECIFICATIONS",
    "特色",
    "功能",
    "尺寸",
    "重量",
    "材質",
    "配件",
    "承重",
    "載重",
    "Load Limit",
    "產品特點",
    "技術參數",
)


def chunk_catalog_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    """
    型錄導向的文字切分

    Args:
        text: 原始文字
        max_chars: 最大字元數
        overlap: 重疊字元數

    Returns:
        切分後的文字片段列表
    """
    if not text:
        return []

    # 清理並正規化文字
    lines = _clean_lines(text.split("\n"))

    # 提取規格表區塊
    spec_chunks, remaining = _extract_spec_blocks(lines)

    # 按標題分段
    sections = _split_sections(remaining)

    # 組裝片段
    chunks: List[str] = []
    chunks.extend(spec_chunks)

    for section in sections:
        chunks.extend(_pack_chunks(section, max_chars=max_chars, overlap=overlap))

    return chunks


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 200) -> List[str]:
    """
    通用文字切分（用於非型錄文件）

    Args:
        text: 原始文字
        max_chars: 最大字元數
        overlap: 重疊字元數

    Returns:
        切分後的文字片段列表
    """
    if not text:
        return []

    paragraphs = _clean_lines(text.split("\n"))
    return _pack_chunks(paragraphs, max_chars=max_chars, overlap=overlap)


def _clean_lines(lines: List[str]) -> List[str]:
    """清理並正規化行"""
    cleaned: List[str] = []
    for line in lines:
        line = _normalize_units(line.strip())
        if not line:
            continue
        # 過濾雜訊
        if any(key in line for key in _NOISE_KEYWORDS):
            continue
        cleaned.append(line)
    return cleaned


def _normalize_units(text: str) -> str:
    """正規化單位"""
    return (
        text.replace("㎏", "kg")
        .replace("ＫＧ", "kg")
        .replace("ｋｇ", "kg")
        .replace("公斤", "kg")
        .replace("公分", "cm")
        .replace("公厘", "mm")
        .replace("公尺", "m")
        .replace("磅", "lbs")
    )


def _extract_spec_blocks(lines: List[str]) -> Tuple[List[str], List[str]]:
    """
    提取規格表區塊

    Returns:
        (規格片段列表, 剩餘行)
    """
    spec_chunks: List[str] = []
    remaining: List[str] = []
    in_spec_block = False
    current_block: List[str] = []

    for line in lines:
        # 檢測規格表開始
        if any(kw in line for kw in ["SPECIFICATIONS", "規格", "技術參數"]):
            in_spec_block = True
            current_block = [line]
            continue

        if in_spec_block:
            # 檢測規格表結束（遇到新標題或空行連續）
            if _is_heading(line) and "規格" not in line and "SPEC" not in line:
                if current_block:
                    spec_chunks.append("\n".join(current_block))
                    current_block = []
                in_spec_block = False
                remaining.append(line)
            else:
                current_block.append(line)
        else:
            remaining.append(line)

    # 處理最後一個規格塊
    if current_block:
        spec_chunks.append("\n".join(current_block))

    return spec_chunks, remaining


def _split_sections(lines: List[str]) -> List[List[str]]:
    """按標題分段"""
    sections: List[List[str]] = []
    current: List[str] = []
    last_heading = ""

    for line in lines:
        # 檢測標題
        if _is_heading(line):
            if current:
                sections.append(current)
                current = []
            last_heading = line
            current.append(line)
            continue

        # 檢測型號行（如 "Model 28"）
        if _looks_like_model_line(line) and current:
            sections.append(current)
            current = []
            if last_heading:
                current.append(last_heading)
            current.append(line)
            continue

        current.append(line)

    if current:
        sections.append(current)

    return sections


def _is_heading(line: str) -> bool:
    """判斷是否為標題"""
    if not line:
        return False

    # 檢查標題關鍵字
    if any(kw in line for kw in _HEADING_KEYWORDS):
        return True

    # 檢查是否全大寫（英文標題特徵）
    if line.isupper() and len(line) > 2:
        return True

    # 檢查是否有標題符號
    if re.match(r'^[▪●■◆►]\s*\w+', line):
        return True

    return False


def _looks_like_model_line(line: str) -> bool:
    """判斷是否為型號行"""
    return bool(re.search(r'(Model|型號)\s*[:\s]*[A-Z0-9\-]+', line, re.IGNORECASE))


def _pack_chunks(paragraphs: List[str], max_chars: int, overlap: int) -> List[str]:
    """打包段落為片段（帶重疊）"""
    if not paragraphs:
        return []

    chunks: List[str] = []
    current = ""
    overlap_buffer = ""

    for para in paragraphs:
        candidate = current + "\n" + para if current else para

        if len(candidate) > max_chars and current:
            # 儲存當前片段
            chunks.append(current)

            # 計算重疊緩衝
            if len(current) > overlap:
                overlap_buffer = current[-overlap:]
            else:
                overlap_buffer = current

            # 開始新片段（帶重疊）
            current = overlap_buffer + "\n" + para
        else:
            current = candidate

    # 添加最後一個片段
    if current:
        chunks.append(current)

    return chunks
