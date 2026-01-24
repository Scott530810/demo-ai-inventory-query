"""
配置管理模組
集中管理所有系統配置、環境變數和資料庫 Schema
"""

import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """資料庫配置"""
    host: str
    database: str
    user: str
    password: str
    port: int

    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """從環境變數載入配置"""
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'ambulance_inventory'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'demo123'),
            port=int(os.getenv('DB_PORT', '5432'))
        )

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式（用於 psycopg2）"""
        return {
            'host': self.host,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'port': self.port
        }


@dataclass
class OllamaConfig:
    """Ollama 配置"""
    host: str
    model: str
    timeout: int = 120

    @classmethod
    def from_env(cls) -> 'OllamaConfig':
        """從環境變數載入配置"""
        return cls(
            host=os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434'),
            model=os.getenv('OLLAMA_MODEL', 'llama3:70b'),
            timeout=int(os.getenv('OLLAMA_TIMEOUT', '120'))
        )


# 資料庫 Schema 定義
DATABASE_SCHEMA = """
資料表名稱: inventory

欄位說明:
- product_id (VARCHAR): 產品編號，如 AED-001
- product_name (VARCHAR): 產品名稱
- category (VARCHAR): 分類（AED除顫器、擔架設備、氧氣設備、監視器、抽吸設備、呼吸設備、固定器材、急救包、車內設備、防護用品、通訊設備）
- brand (VARCHAR): 廠牌
- model (VARCHAR): 型號
- specifications (TEXT): 規格說明
- stock_quantity (INTEGER): 庫存數量
- unit_price (DECIMAL): 單價（新台幣）
- supplier (VARCHAR): 供應商
- last_updated (TIMESTAMP): 最後更新時間

常見分類:
- AED除顫器: Philips, ZOLL, Mindray 等品牌
- 擔架設備: Ferno, Spencer 等品牌
- 氧氣設備: Luxfer, Precision Medical 等
- 監視器: Mindray, Masimo, GE 等

視圖:
- low_stock_alert: 顯示庫存少於10件的商品
- category_summary: 各分類的統計資訊
"""

# SQL 生成的系統提示詞
SQL_GENERATION_PROMPT = f"""你是 PostgreSQL 專家。根據使用者問題產生單一 SQL 查詢。

{DATABASE_SCHEMA}

硬性規則:
1. 只輸出 SQL，不能有解釋、Markdown、註解或多餘文字。
2. 只能輸出一條查詢，不能含分號。
3. 僅允許 SELECT，禁止任何寫入或 DDL 操作。
4. 只能使用這個表與欄位:
   - 表: inventory
   - 欄位: product_id, product_name, category, brand, model, specifications, stock_quantity, unit_price, supplier, last_updated
5. 模糊比對請用 ILIKE '%關鍵字%'.
6. 若問題涉及庫存，預設加上 stock_quantity > 0.
7. 若問題涉及價格:
   - 「最便宜/最低/較低」使用 ORDER BY unit_price ASC
   - 「最貴/最高/較高」使用 ORDER BY unit_price DESC
8. 若問題涉及庫存高低，使用 ORDER BY stock_quantity DESC.
9. 除非問題明確要求全部結果，預設加 LIMIT 50.

輸出格式:
<單行 SQL 查詢>
"""

# 回應生成的系統提示詞
RESPONSE_GENERATION_PROMPT = """你是專業的救護/醫療設備庫存顧問。請只根據提供的查詢結果回答，不可編造。使用繁體中文。

輸出格式(結果非空時只輸出兩段):
1) 摘要: 1 句總結。
2) 主要結果: 最多列 5 筆，使用項目符號，每筆只包含結果裡有的欄位。

規則:
- 不要輸出 SQL、JSON 或任何系統描述。
- 不要提供額外建議或延伸說明。
- 控制在 200 字內，語氣簡潔專業。
"""

# Demo 查詢問題 - 設計為明確且單一目標的問題
DEMO_QUESTIONS = [
    "請列出所有有庫存的AED除顫器，包含品牌、型號和庫存數量",
    "請列出所有擔架設備的品牌、型號和庫存數量",
    "請列出單價低於50000元的監視器，包含品牌、型號和價格",
    "請列出庫存數量低於10件的商品，包含產品名稱、分類和庫存數量",
    "請列出所有Philips品牌的產品，包含名稱、型號和單價",
]
