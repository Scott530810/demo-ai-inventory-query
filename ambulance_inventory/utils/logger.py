"""
日誌管理模組
提供統一的日誌系統
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    設置日誌記錄器

    Args:
        name: Logger 名稱
        level: 日誌級別
        format_string: 自訂格式字串

    Returns:
        配置好的 Logger 實例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重複添加 handler
    if logger.handlers:
        return logger

    # 創建控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # 設置格式
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    獲取已存在的 logger

    Args:
        name: Logger 名稱

    Returns:
        Logger 實例
    """
    return logging.getLogger(name)
