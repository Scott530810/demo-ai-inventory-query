"""
輸入驗證工具
提供 SQL 驗證和安全檢查
"""

import re
from typing import Tuple


def is_dangerous_sql(sql: str) -> Tuple[bool, str]:
    """
    檢查 SQL 是否包含危險操作

    Args:
        sql: SQL 查詢字串

    Returns:
        (是否危險, 原因說明)
    """
    sql_upper = sql.upper()

    # 危險關鍵字列表
    dangerous_keywords = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER',
        'CREATE', 'INSERT', 'UPDATE', 'GRANT',
        'REVOKE', 'EXECUTE', 'EXEC'
    ]

    for keyword in dangerous_keywords:
        # 使用正則確保是獨立的關鍵字（不是部分匹配）
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            return True, f"包含危險操作: {keyword}"

    # 檢查是否有分號（可能是 SQL 注入）
    if sql.count(';') > 1:
        return True, "包含多個 SQL 語句"

    # 檢查註解符號（可能試圖繞過驗證）
    if '--' in sql or '/*' in sql:
        return True, "包含 SQL 註解符號"

    return False, ""


def validate_sql(sql: str) -> Tuple[bool, str]:
    """
    驗證 SQL 的基本格式和安全性

    Args:
        sql: SQL 查詢字串

    Returns:
        (是否有效, 錯誤訊息)
    """
    if not sql or not sql.strip():
        return False, "SQL 為空"

    sql_stripped = sql.strip()

    # 檢查是否以 SELECT 開頭（只允許查詢）
    if not sql_stripped.upper().startswith('SELECT'):
        return False, "只允許 SELECT 查詢"

    # 檢查危險操作
    is_dangerous, reason = is_dangerous_sql(sql_stripped)
    if is_dangerous:
        return False, f"安全檢查失敗: {reason}"

    # 檢查基本語法
    if 'FROM' not in sql_stripped.upper():
        return False, "缺少 FROM 子句"

    # 檢查括號匹配
    if sql_stripped.count('(') != sql_stripped.count(')'):
        return False, "括號不匹配"

    return True, ""


def clean_sql(sql: str) -> str:
    """
    清理 SQL 字串
    移除 Markdown 標記、角括號和多餘空白

    Args:
        sql: 原始 SQL 字串

    Returns:
        清理後的 SQL
    """
    # 移除 Markdown 標記
    sql = sql.replace('```sql', '').replace('```', '').strip()

    # 移除某些模型會加的角括號包裹 (如 <SELECT ...> 或 <sql>...</sql>)
    sql = re.sub(r'^<\s*', '', sql)  # 移除開頭的 <
    sql = re.sub(r'\s*>$', '', sql)  # 移除結尾的 >
    sql = re.sub(r'^<sql>\s*', '', sql, flags=re.IGNORECASE)  # 移除 <sql>
    sql = re.sub(r'\s*</sql>$', '', sql, flags=re.IGNORECASE)  # 移除 </sql>
    sql = re.sub(r'^<query>\s*', '', sql, flags=re.IGNORECASE)  # 移除 <query>
    sql = re.sub(r'\s*</query>$', '', sql, flags=re.IGNORECASE)  # 移除 </query>

    # 移除可能的引號包裹
    if sql.startswith('"') and sql.endswith('"'):
        sql = sql[1:-1]
    if sql.startswith("'") and sql.endswith("'"):
        sql = sql[1:-1]

    sql = sql.strip()

    # 移除可能的解釋文字（只保留 SQL）
    lines = sql.split('\n')
    sql_lines = []

    for line in lines:
        line = line.strip()
        if line and (
            line.upper().startswith('SELECT') or
            line.upper().startswith('FROM') or
            line.upper().startswith('WHERE') or
            line.upper().startswith('ORDER') or
            line.upper().startswith('GROUP') or
            line.upper().startswith('LIMIT') or
            line.upper().startswith('AND') or
            line.upper().startswith('OR') or
            line.upper().startswith('WITH') or
            'JOIN' in line.upper() or
            ')' in line or '(' in line
        ):
            sql_lines.append(line)

    return ' '.join(sql_lines) if sql_lines else sql
