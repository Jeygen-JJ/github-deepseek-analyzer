import os
from pathlib import Path

import requests


PROJECT_DIR = Path(__file__).parent
ENV_FILE_PATH = PROJECT_DIR / "env.env"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL_NAME = "deepseek-chat"


def load_env_file():
    """读取 env.env 文件，把里面的键值放进环境变量。"""
    if not ENV_FILE_PATH.exists():
        return

    with ENV_FILE_PATH.open("r", encoding="utf-8") as env_file:
        for line in env_file:
            clean_line = line.strip()

            # 跳过空行和注释行。
            if not clean_line or clean_line.startswith("#"):
                continue

            if "=" not in clean_line:
                continue

            key, value = clean_line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


def get_deepseek_api_key():
    """获取 DeepSeek API Key，但不要在命令行打印它。"""
    load_env_file()
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError("找不到 DEEPSEEK_API_KEY，请检查 env.env 文件。")

    return api_key


def ask_deepseek(prompt):
    """调用 DeepSeek API，并返回模型生成的文本。"""
    try:
        api_key = get_deepseek_api_key()
    except ValueError as error:
        return f"请求失败：{error}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    request_body = {
        "model": DEEPSEEK_MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "你是一个帮助 Python 初学者学习开源项目的助手。请严格输出合法 JSON。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=request_body,
            timeout=120,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return "请求失败：DeepSeek API 响应超时。可以稍后重试。"
    except requests.exceptions.HTTPError as error:
        status_code = error.response.status_code if error.response else "未知"

        if status_code == 401:
            return "请求失败：DeepSeek API Key 无效或没有权限，请检查 env.env。"

        if status_code == 429:
            return "请求失败：DeepSeek API 请求过于频繁或额度受限，请稍后再试。"

        error_text = error.response.text if error.response else str(error)
        return f"请求失败：DeepSeek API 返回状态码 {status_code}。错误信息：{error_text}"
    except requests.exceptions.ConnectionError:
        return "请求失败：无法连接 DeepSeek API，请检查网络连接。"
    except requests.exceptions.RequestException as error:
        return f"请求失败：{error}"

    response_data = response.json()

    try:
        return response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return "请求成功，但 DeepSeek 响应中没有找到 choices[0].message.content。"
