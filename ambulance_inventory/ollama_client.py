"""
Ollama 客戶端模組
處理與 Ollama API 的通信
"""

import requests
from typing import Optional
import logging

from .config import OllamaConfig
from .utils.logger import get_logger


class OllamaClient:
    """Ollama API 客戶端"""

    def __init__(self, config: OllamaConfig):
        """
        初始化 Ollama 客戶端

        Args:
            config: Ollama 配置
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.api_url = f"{config.host}/api/generate"
        self.tags_url = f"{config.host}/api/tags"

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.1,
        model: Optional[str] = None
    ) -> Optional[str]:
        """
        調用 Ollama 生成文本

        Args:
            prompt: 用戶提示詞
            system_prompt: 系統提示詞
            temperature: 溫度參數 (0.0-1.0)
            model: 使用的模型（可選，不指定則使用預設模型）

        Returns:
            生成的文本，失敗時返回 None
        """
        try:
            # 使用傳入的模型，若無則使用預設模型
            use_model = model if model else self.config.model

            payload = {
                "model": use_model,
                "prompt": prompt,
                "system": system_prompt,
                "temperature": temperature,
                "stream": False
            }

            self.logger.debug(f"調用 Ollama API: {self.api_url} (model: {use_model})")

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()

            result = response.json()
            generated_text = result.get('response', '').strip()

            self.logger.info(f"Ollama 生成成功 ({len(generated_text)} 字符)")

            return generated_text

        except requests.exceptions.ConnectionError:
            self.logger.error(f"無法連接到 Ollama ({self.config.host})")
            print(f"❌ 無法連接到 Ollama ({self.config.host})")
            print("\n請確認:")
            print("  1. Ollama 正在運行（在 Windows 開啟 Ollama）")
            print("  2. 允許外部訪問（設定 OLLAMA_HOST=0.0.0.0）")
            return None

        except requests.exceptions.Timeout:
            self.logger.error("Ollama 回應超時")
            print("⏱️ Ollama 回應超時（模型可能正在載入）")
            return None

        except Exception as e:
            self.logger.error(f"Ollama 錯誤: {str(e)}")
            print(f"❌ Ollama 錯誤: {str(e)}")
            return None

    def test_connection(self) -> bool:
        """
        測試 Ollama 連接

        Returns:
            連接是否成功
        """
        try:
            response = requests.get(self.tags_url, timeout=5)
            response.raise_for_status()

            self.logger.info("Ollama 連接測試成功")
            return True

        except Exception as e:
            self.logger.error(f"Ollama 連接測試失敗: {str(e)}")
            return False

    def get_available_models(self) -> list:
        """
        獲取已安裝的模型列表

        Returns:
            模型名稱列表
        """
        try:
            response = requests.get(self.tags_url, timeout=5)
            response.raise_for_status()

            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]

            self.logger.info(f"找到 {len(model_names)} 個已安裝的模型")

            return model_names

        except Exception as e:
            self.logger.error(f"獲取模型列表失敗: {str(e)}")
            return []

    def is_model_available(self) -> bool:
        """
        檢查目標模型是否可用

        Returns:
            模型是否可用
        """
        models = self.get_available_models()
        return self.config.model in models

    def test_inference(self) -> bool:
        """
        測試模型推理能力

        Returns:
            推理是否成功
        """
        test_prompt = "請用一句話說明什麼是資料庫。"
        response = self.generate(test_prompt, "", 0.7)

        if response and len(response) > 10:
            self.logger.info("Ollama 推理測試成功")
            return True
        else:
            self.logger.error("Ollama 推理測試失敗")
            return False
