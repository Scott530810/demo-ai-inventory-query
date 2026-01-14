#!/usr/bin/env python3
"""
救護車庫存查詢系統 - Ollama 本地端版本
使用本地 Ollama + qwen2.5:32b 模型
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
import requests
from datetime import datetime
from decimal import Decimal

# ============================================
# 配置設定
# ============================================

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'ambulance_inventory'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'demo123'),
    'port': int(os.getenv('DB_PORT', '5432'))
}

# Ollama 設定
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:32b')

# ============================================
# 資料庫 Schema
# ============================================

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

# ============================================
# 輔助函數
# ============================================

def decimal_to_float(obj):
    """將 Decimal 類型轉換為 float，用於 JSON 序列化"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

# ============================================
# Ollama API 調用
# ============================================

def call_ollama(prompt, system_prompt="", temperature=0.1):
    """調用本地 Ollama API"""
    try:
        url = f"{OLLAMA_HOST}/api/generate"
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "system": system_prompt,
            "temperature": temperature,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', '').strip()
        
    except requests.exceptions.ConnectionError:
        print(f"❌ 無法連接到 Ollama ({OLLAMA_HOST})")
        print("\n請確認:")
        print("  1. Ollama 正在運行（在 Windows 開啟 Ollama）")
        print("  2. 允許外部訪問（設定 OLLAMA_HOST=0.0.0.0）")
        return None
    except requests.exceptions.Timeout:
        print("⏱️ Ollama 回應超時（模型可能正在載入）")
        return None
    except Exception as e:
        print(f"❌ Ollama 錯誤: {str(e)}")
        return None

# ============================================
# 主查詢邏輯
# ============================================

def query_with_ollama(question):
    """使用 Ollama 生成 SQL 並解釋結果"""
    
    # 步驟1: 生成 SQL
    system_prompt = f"""你是一個 PostgreSQL 專家。根據使用者的問題生成 SQL 查詢。

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

    print("🤖 正在請求 Ollama 生成 SQL...")
    print(f"   模型: {OLLAMA_MODEL}")
    
    sql_query = call_ollama(question, system_prompt, temperature=0.1)
    
    if not sql_query:
        return None, None
    
    # 清理 SQL（移除可能的 Markdown 標記）
    sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
    
    # 移除可能的解釋文字（只保留 SQL）
    lines = sql_query.split('\n')
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
            'JOIN' in line.upper() or
            ')' in line or '(' in line
        ):
            sql_lines.append(line)
    
    sql_query = ' '.join(sql_lines) if sql_lines else sql_query
    
    print(f"\n📝 生成的 SQL:")
    print(f"{sql_query}\n")
    
    # 步驟2: 執行 SQL
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql_query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"✅ 查詢成功，找到 {len(results)} 筆結果\n")
        
    except Exception as e:
        print(f"❌ SQL 執行錯誤: {str(e)}")
        print("   Ollama 生成的 SQL 可能有誤，正在重試...\n")
        return sql_query, None
    
    # 步驟3: 用 Ollama 生成友善回應
    if results:
        print("🤖 正在請求 Ollama 生成回應...")
        
        # 限制結果數量避免 context 過大
        limited_results = results[:20] if len(results) > 20 else results

        # 轉換為可讀格式 (使用 default 處理 Decimal 類型)
        results_text = json.dumps(limited_results, ensure_ascii=False, indent=2, default=decimal_to_float)
        
        system_prompt = """你是一位專業的救護車設備專家，負責協助查詢庫存資訊。
請用專業但友善的口吻回答問題。使用繁體中文。

回答要求:
1. 簡潔明瞭，重點突出
2. 包含關鍵資訊: 數量、價格、廠牌
3. 適當使用項目符號或編號
4. 如果資料很多，可以分類整理
5. 提供有用的補充建議（如低庫存警示、價格比較等）"""
        
        prompt = f"""使用者問題: {question}

查詢結果:
{results_text}

請根據查詢結果，用友善專業的方式回答使用者的問題。"""
        
        answer = call_ollama(prompt, system_prompt, temperature=0.7)
        
        if not answer:
            # 如果 Ollama 回應失敗，提供基本格式化輸出
            answer = f"查詢結果共 {len(results)} 筆:\n\n"
            for i, row in enumerate(limited_results[:10], 1):
                answer += f"{i}. "
                answer += " | ".join([f"{k}: {v}" for k, v in row.items()])
                answer += "\n"
    else:
        answer = "抱歉，沒有找到相關資料。"
    
    return sql_query, answer

# ============================================
# 查詢介面
# ============================================

def query_inventory(question):
    """執行庫存查詢"""
    print(f"\n{'='*70}")
    print(f"❓ 問題: {question}")
    print(f"🤖 使用模型: {OLLAMA_MODEL}")
    print(f"{'='*70}\n")
    
    sql, answer = query_with_ollama(question)
    
    if sql and answer:
        print(f"💬 AI 回應:")
        print(f"{answer}\n")
        return True
    elif sql and not answer:
        print("⚠️ SQL 生成成功但執行失敗\n")
        return False
    else:
        print("❌ 查詢失敗\n")
        return False

# ============================================
# 互動模式
# ============================================

def interactive_mode():
    """互動查詢模式"""
    print("\n" + "="*70)
    print("  🚀 進入互動模式（本地 Ollama 版本）")
    print(f"  模型: {OLLAMA_MODEL}")
    print(f"  主機: {OLLAMA_HOST}")
    print("  輸入 'exit' 或 'quit' 離開")
    print("="*70 + "\n")
    
    # 測試 Ollama 連接
    print("🔍 測試 Ollama 連接...")
    test_response = call_ollama("hello", "", 0.1)
    if test_response:
        print("✅ Ollama 連接成功！\n")
    else:
        print("❌ Ollama 連接失敗，請檢查設定\n")
        return
    
    while True:
        try:
            question = input("\n💭 請輸入您的問題: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', '離開', '退出']:
                print("\n👋 再見！")
                break
            
            query_inventory(question)
            
        except KeyboardInterrupt:
            print("\n\n👋 再見！")
            break
        except Exception as e:
            print(f"\n❌ 發生錯誤: {str(e)}")

# ============================================
# Demo 模式
# ============================================

def demo_mode():
    """執行預設的 Demo 查詢"""
    print("\n" + "="*70)
    print("  🎬 Demo 模式（本地 Ollama 版本）")
    print(f"  模型: {OLLAMA_MODEL}")
    print("="*70)
    
    # 測試 Ollama 連接
    print("\n🔍 測試 Ollama 連接...")
    test_response = call_ollama("hello", "", 0.1)
    if not test_response:
        print("❌ Ollama 連接失敗")
        print("\n請確認:")
        print("  1. Ollama 正在運行")
        print("  2. 模型已下載: ollama pull qwen2.5:32b")
        return
    print("✅ Ollama 連接成功！\n")
    
    demo_questions = [
        "請問AED除顫器還有哪幾款有庫存？",
        "我們公司還有多少擔架？",
        "預算5萬以內有什麼監視器可以買？",
        "哪些商品庫存不足10件？需要補貨",
        "Philips飛利浦的產品有哪些？總價值多少？",
    ]
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{'='*70}")
        print(f"Demo {i}/{len(demo_questions)}")
        print(f"{'='*70}")

        # 檢查是否在互動式終端中
        import sys
        if sys.stdin.isatty():
            input("按 Enter 繼續...")
        else:
            print("自動繼續...\n")

        query_inventory(question)
    
    print("\n" + "="*70)
    print("  ✅ Demo 完成！")
    print("="*70 + "\n")

# ============================================
# 系統檢查
# ============================================

def check_system():
    """檢查系統狀態"""
    print("\n" + "="*70)
    print("  🔍 系統狀態檢查")
    print("="*70 + "\n")
    
    # 檢查資料庫
    print("1️⃣ 檢查資料庫連接...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventory;")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"   ✅ 資料庫連接成功！共 {count} 項商品\n")
    except Exception as e:
        print(f"   ❌ 資料庫連接失敗: {str(e)}\n")
        return False
    
    # 檢查 Ollama
    print("2️⃣ 檢查 Ollama 連接...")
    print(f"   主機: {OLLAMA_HOST}")
    print(f"   模型: {OLLAMA_MODEL}")
    
    try:
        # 測試連接
        url = f"{OLLAMA_HOST}/api/tags"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        models = response.json().get('models', [])
        model_names = [m['name'] for m in models]
        
        print(f"   ✅ Ollama 連接成功！")
        print(f"   📦 已安裝的模型: {', '.join(model_names)}")
        
        if OLLAMA_MODEL in model_names:
            print(f"   ✅ 目標模型 {OLLAMA_MODEL} 已就緒\n")
        else:
            print(f"   ⚠️ 目標模型 {OLLAMA_MODEL} 未安裝")
            print(f"   請執行: ollama pull {OLLAMA_MODEL}\n")
            return False
            
    except Exception as e:
        print(f"   ❌ Ollama 連接失敗: {str(e)}")
        print("\n   請確認:")
        print("   • Ollama 正在運行")
        print("   • 允許外部訪問（OLLAMA_HOST=0.0.0.0）\n")
        return False
    
    # 測試查詢
    print("3️⃣ 測試 Ollama 推理能力...")
    test_prompt = "請用一句話說明什麼是資料庫。"
    response = call_ollama(test_prompt, "", 0.7)
    
    if response:
        print(f"   ✅ Ollama 推理測試成功")
        print(f"   回應: {response[:100]}...\n")
    else:
        print(f"   ❌ Ollama 推理測試失敗\n")
        return False
    
    print("="*70)
    print("  ✅ 系統檢查完成！一切正常")
    print("="*70 + "\n")
    return True

# ============================================
# 主程式
# ============================================

def main():
    import sys
    
    print(f"\n{'='*70}")
    print(f"  救護車庫存查詢系統 - Ollama 本地端版本")
    print(f"{'='*70}")
    print(f"資料庫: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"Ollama: {OLLAMA_HOST}")
    print(f"模型: {OLLAMA_MODEL}")
    print(f"{'='*70}\n")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--demo':
            demo_mode()
        elif sys.argv[1] == '--interactive':
            interactive_mode()
        elif sys.argv[1] == '--check':
            check_system()
        else:
            print("用法:")
            print("  python test_llm_query_ollama.py --demo         # 執行 Demo")
            print("  python test_llm_query_ollama.py --interactive  # 互動模式")
            print("  python test_llm_query_ollama.py --check        # 系統檢查")
            print("\n環境變數:")
            print("  OLLAMA_HOST=http://host.docker.internal:11434  # Ollama 位址")
            print("  OLLAMA_MODEL=qwen2.5:32b                        # 使用的模型")
    else:
        print("請選擇模式:")
        print("1. 系統檢查")
        print("2. 執行 Demo")
        print("3. 互動模式")
        
        choice = input("\n請選擇 (1/2/3): ").strip()
        
        if choice == '1':
            check_system()
        elif choice == '3':
            interactive_mode()
        else:
            demo_mode()

if __name__ == "__main__":
    main()
