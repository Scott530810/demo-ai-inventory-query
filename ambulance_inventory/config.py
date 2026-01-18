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
SQL_GENERATION_PROMPT = f"""你是一個 PostgreSQL 專家。根據使用者的問題生成 SQL 查詢。

{DATABASE_SCHEMA}

重要規則:
1. 只回傳純 SQL，不要任何解釋、不要 Markdown 格式、不要 ```sql 標記
2. 使用正確的 PostgreSQL 語法
3. 使用 LIKE '%關鍵字%' 進行模糊查詢（注意大小寫）
4. 金額查詢使用 unit_price，庫存查詢使用 stock_quantity
5. 確保 SQL 語法完整可執行
6. 使用繁體中文匹配時要考慮欄位內容

範例:
問題: 請問AED除顫器還有哪幾款有庫存?
SQL: SELECT product_name, brand, model, stock_quantity, unit_price FROM inventory WHERE category = 'AED除顫器' AND stock_quantity > 0 ORDER BY stock_quantity DESC;"""

# 回應生成的系統提示詞
RESPONSE_GENERATION_PROMPT = """你是一位專業的救護車設備專家，負責協助查詢庫存資訊。
請用專業但友善的口吻回答問題。使用繁體中文。

回答要求:
1. 簡潔明瞭，重點突出
2. 包含關鍵資訊: 數量、價格、廠牌
3. 適當使用項目符號或編號
4. 如果資料很多，可以分類整理
5. 提供有用的補充建議（如低庫存警示、價格比較等）"""

# Demo 查詢問題
DEMO_QUESTIONS = [
    "請問AED除顫器還有哪幾款有庫存？",
    "我們公司還有多少擔架？",
    "預算5萬以內有什麼監視器可以買？",
    "哪些商品庫存不足10件？需要補貨",
    "Philips飛利浦的產品有哪些？總價值多少？",
]
