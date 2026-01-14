"""
救護車庫存查詢系統 - 主程式入口
Ollama 本地端版本 v2.0
"""

import sys
import logging

from .config import DatabaseConfig, OllamaConfig
from .database import DatabaseClient
from .ollama_client import OllamaClient
from .query_engine import QueryEngine
from .ui import interactive_mode, demo_mode, check_system
from .utils.logger import setup_logger


def print_banner(db_config: DatabaseConfig, ollama_config: OllamaConfig):
    """顯示系統啟動橫幅"""
    print(f"\n{'='*70}")
    print(f"  救護車庫存查詢系統 - Ollama 本地端版本 v2.0")
    print(f"{'='*70}")
    print(f"資料庫: {db_config.host}:{db_config.port}/{db_config.database}")
    print(f"Ollama: {ollama_config.host}")
    print(f"模型: {ollama_config.model}")
    print(f"{'='*70}\n")


def print_usage():
    """顯示使用說明"""
    print("用法:")
    print("  python -m ambulance_inventory.main --demo         # 執行 Demo")
    print("  python -m ambulance_inventory.main --interactive  # 互動模式")
    print("  python -m ambulance_inventory.main --check        # 系統檢查")
    print("\n環境變數:")
    print("  OLLAMA_HOST=http://host.docker.internal:11434  # Ollama 位址")
    print("  OLLAMA_MODEL=qwen3:30b                          # 使用的模型")
    print("  DB_HOST=localhost                                # 資料庫主機")
    print("  DB_PORT=5432                                     # 資料庫端口")


def main():
    """主程式入口"""
    # 設置日誌
    setup_logger('ambulance_inventory', logging.INFO)
    logger = logging.getLogger('ambulance_inventory')

    # 載入配置
    db_config = DatabaseConfig.from_env()
    ollama_config = OllamaConfig.from_env()

    # 顯示橫幅
    print_banner(db_config, ollama_config)

    # 初始化組件
    db_client = DatabaseClient(db_config)
    ollama_client = OllamaClient(ollama_config)
    query_engine = QueryEngine(db_client, ollama_client)

    # 解析命令列參數
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == '--demo':
            demo_mode(query_engine, ollama_client)

        elif command == '--interactive':
            interactive_mode(query_engine, ollama_client)

        elif command == '--check':
            check_system(db_client, ollama_client)

        else:
            print(f"❌ 未知命令: {command}\n")
            print_usage()

    else:
        # 互動式選單
        print("請選擇模式:")
        print("1. 系統檢查")
        print("2. 執行 Demo")
        print("3. 互動模式")

        choice = input("\n請選擇 (1/2/3): ").strip()

        if choice == '1':
            check_system(db_client, ollama_client)
        elif choice == '3':
            interactive_mode(query_engine, ollama_client)
        else:
            demo_mode(query_engine, ollama_client)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程式已中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 發生錯誤: {str(e)}")
        sys.exit(1)
