"""
Python Client for DGX SPARK Server
從 Windows 11 連線到 SPARK 服務器的 Python 客戶端

Usage:
    # Interactive mode
    python spark_client.py --interactive

    # Single query
    python spark_client.py --query "請問AED除顫器還有哪幾款有庫存？"

    # Health check
    python spark_client.py --health
"""

import requests
import argparse
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass
import sys


@dataclass
class SparkConfig:
    """SPARK 服務器配置"""
    host: str = "SPARK_IP_HERE"  # 替換為實際 IP
    port: int = 8000
    timeout: int = 60

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def health_url(self) -> str:
        return f"{self.base_url}/health"

    @property
    def query_url(self) -> str:
        return f"{self.base_url}/query"

    @property
    def docs_url(self) -> str:
        return f"{self.base_url}/docs"


class SparkClient:
    """SPARK 服務器客戶端"""

    def __init__(self, config: SparkConfig):
        self.config = config
        self.session = requests.Session()

    def test_connection(self) -> bool:
        """測試與 SPARK 服務器的連接"""
        print(f"🔍 Testing connection to {self.config.host}:{self.config.port}...")

        try:
            response = self.session.get(
                self.config.health_url,
                timeout=5
            )
            response.raise_for_status()

            health_data = response.json()

            if health_data.get("status") == "healthy":
                print("✅ Connection successful!")
                print(f"   Database: {'✅' if health_data.get('database') else '❌'}")
                print(f"   Ollama: {'✅' if health_data.get('ollama') else '❌'}")
                print(f"   Model: {health_data.get('model')}")
                print(f"   Version: {health_data.get('version')}")
                return True
            else:
                print("⚠️  Server is unhealthy")
                return False

        except requests.exceptions.ConnectionError:
            print(f"❌ Failed to connect to SPARK server at {self.config.host}:{self.config.port}")
            print("\n💡 Troubleshooting:")
            print(f"   1. Check if SPARK IP is correct: {self.config.host}")
            print("   2. Ensure API server is running on SPARK")
            print(f"   3. Check firewall allows port {self.config.port}")
            print(f"   4. Test with: ping {self.config.host}")
            return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def query(self, question: str) -> Optional[Dict[str, Any]]:
        """執行查詢"""
        print(f"\n💭 Question: {question}")
        print("Sending to SPARK server...")

        try:
            response = self.session.post(
                self.config.query_url,
                json={"question": question},
                timeout=self.config.timeout
            )
            response.raise_for_status()

            result = response.json()

            if result.get("success"):
                print("\n✅ Query Successful!")
                print("=" * 60)
                print(f"\n📊 SQL Query:")
                print(result.get("sql"))
                print(f"\n💡 Answer:")
                print(result.get("answer"))
                print("=" * 60)
            else:
                print(f"\n❌ Query Failed")
                print(f"Error: {result.get('error')}")

            return result

        except requests.exceptions.Timeout:
            print("❌ Query timeout - server took too long to respond")
            return None

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def interactive_mode(self):
        """互動模式"""
        print("\n🎮 Starting Interactive Mode")
        print("Type 'exit' or 'quit' to exit, 'help' for demo queries")
        print("=" * 60)

        demo_queries = [
            "請問AED除顫器還有哪幾款有庫存？",
            "請問輪椅有哪些品牌？",
            "請問救護車擔架有哪些型號？",
            "請問有哪些設備的庫存數量少於10件？",
            "請問設備表中有哪些類別？"
        ]

        while True:
            try:
                user_input = input("\n💭 Your question: ").strip()

                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\n👋 Goodbye!")
                    break

                if user_input.lower() in ["help", "h", "?"]:
                    print("\n📚 Demo Queries:")
                    for i, query in enumerate(demo_queries, 1):
                        print(f"{i}. {query}")
                    continue

                if not user_input:
                    print("⚠️  Please enter a question")
                    continue

                self.query(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break

    def show_info(self):
        """顯示服務器資訊"""
        print("\n📋 SPARK Server Information")
        print("=" * 60)
        print(f"Host: {self.config.host}")
        print(f"Port: {self.config.port}")
        print(f"Base URL: {self.config.base_url}")
        print(f"Health Check: {self.config.health_url}")
        print(f"API Docs: {self.config.docs_url}")
        print("=" * 60)

    def demo_mode(self):
        """Demo 模式 - 執行預設的中文查詢"""
        demo_queries = [
            "AED除顫器有庫存嗎",
            "輪椅有哪些品牌",
            "擔架有哪些型號",
            "庫存少於10件的設備",
            "設備有哪些類別"
        ]

        print("\n📚 Demo Queries (中文示範查詢):")
        print("=" * 60)
        for i, query in enumerate(demo_queries, 1):
            print(f"  {i}. {query}")
        print(f"  6. Run all (執行全部)")
        print(f"  0. Cancel (取消)")
        print("=" * 60)

        try:
            choice = input("\nYour choice (0-6): ").strip()

            if choice == "0" or not choice:
                print("Cancelled")
                return

            if choice == "6":
                print("\n🚀 Running all demo queries...")
                for query in demo_queries:
                    self.query(query)
                    print("\n" + "-" * 60 + "\n")
            elif choice in ["1", "2", "3", "4", "5"]:
                idx = int(choice) - 1
                self.query(demo_queries[idx])
            else:
                print("❌ Invalid choice")

        except KeyboardInterrupt:
            print("\nCancelled")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description="SPARK Server Client - Windows 11 遠端連線工具"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="SPARK_IP_HERE",
        help="SPARK server IP address"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="SPARK server port (default: 8000)"
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive mode"
    )

    parser.add_argument(
        "--query",
        "-q",
        type=str,
        help="Execute a single query"
    )

    parser.add_argument(
        "--health",
        action="store_true",
        help="Check server health"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Show server information"
    )

    parser.add_argument(
        "--demo",
        "-d",
        action="store_true",
        help="Run demo queries (中文示範查詢)"
    )

    args = parser.parse_args()

    # Create configuration
    config = SparkConfig(host=args.host, port=args.port)

    # Check if host is configured
    if config.host == "SPARK_IP_HERE":
        print("❌ Error: Please configure SPARK IP address!")
        print("\nOptions:")
        print("1. Use --host parameter: python spark_client.py --host 192.168.1.100")
        print("2. Edit spark_client.py and replace SPARK_IP_HERE with actual IP")
        sys.exit(1)

    # Create client
    client = SparkClient(config)

    # Show info
    if args.info:
        client.show_info()
        return

    # Test connection first
    print(f"🚀 Ambulance Inventory Query Client - Windows 11")
    print(f"Connecting to SPARK Server: {config.host}:{config.port}")
    print("=" * 60)

    if not client.test_connection():
        sys.exit(1)

    # Execute based on arguments
    if args.health:
        # Already tested in test_connection
        pass

    elif args.query:
        client.query(args.query)

    elif args.demo:
        client.demo_mode()

    elif args.interactive:
        client.interactive_mode()

    else:
        # Show menu
        print("\n📋 Choose an option:")
        print("1. Interactive mode (互動模式)")
        print("2. Demo queries (中文示範查詢)")
        print("3. Health check (健康檢查)")
        print("4. Show server info (伺服器資訊)")
        print("5. Exit (離開)")

        choice = input("\nYour choice (1-5): ").strip()

        if choice == "1":
            client.interactive_mode()
        elif choice == "2":
            client.demo_mode()
        elif choice == "3":
            client.test_connection()
        elif choice == "4":
            client.show_info()
        elif choice == "5":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")

    print("\n✨ Script completed")


if __name__ == "__main__":
    main()
