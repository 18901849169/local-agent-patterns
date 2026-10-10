import json
import os
from typing import Dict, List
from urllib.request import Request, urlopen

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    pass
else:
    load_dotenv()


class HelloAgentsLLM:
    """使用本地 Ollama 调用大语言模型。"""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        timeout: int | None = None,
    ):
        self.model = model or os.getenv("LLM_MODEL_ID")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.timeout = timeout or int(os.getenv("LLM_TIMEOUT", "120"))

        if not self.model or not self.base_url:
            raise ValueError(
                "LLM_MODEL_ID and LLM_BASE_URL must be configured as environment variables"
            )

    def think(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
    ) -> str:
        print(f"正在调用 {self.model} 模型...")

        prompt = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in messages
        )

        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }).encode("utf-8")

        request = Request(
            self.base_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request, timeout=self.timeout) as response:
            result = json.load(response)

        print("大语言模型响应成功。")
        return result["response"]


if __name__ == "__main__":
    try:
        llmClient = HelloAgentsLLM()

        exampleMessages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that writes Python code.",
            },
            {
                "role": "user",
                "content": "写一个快速排序算法",
            },
        ]

        print("--- 调用 LLM ---")
        responseText = llmClient.think(exampleMessages)

        if responseText:
            print("\n--- 完整模型响应 ---")
            print(responseText)

    except ValueError as error:
        print(error)
