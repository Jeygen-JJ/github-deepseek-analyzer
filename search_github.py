import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlencode

import requests


GITHUB_SEARCH_API_URL = "https://api.github.com/search/repositories"

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
SEARCH_RESULTS_PATH = DATA_DIR / "search_results.json"


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def build_search_query(keyword, language, min_stars):
    """拼接 GitHub Search API 需要的 q 参数。"""
    return f"{keyword} language:{language} stars:>{min_stars}"


def build_request_url(keyword, language, min_stars, top_k):
    """生成最终请求地址，方便打印和排查。"""
    request_params = {
        "q": build_search_query(keyword, language, min_stars),
        "sort": "stars",
        "order": "desc",
        "per_page": top_k,
    }
    return f"{GITHUB_SEARCH_API_URL}?{urlencode(request_params)}"


def get_license_name(repo):
    """从 GitHub 返回的数据中取出 license.name。"""
    license_info = repo.get("license")

    if license_info is None:
        return None

    return license_info.get("name")


def extract_repo_info(repo):
    """只保留我们后续分析真正需要的字段。"""
    return {
        "full_name": repo.get("full_name"),
        "description": repo.get("description"),
        "stargazers_count": repo.get("stargazers_count", 0),
        "open_issues_count": repo.get("open_issues_count", 0),
        "language": repo.get("language"),
        "html_url": repo.get("html_url"),
        "updated_at": repo.get("updated_at"),
        "license_name": get_license_name(repo),
        "archived": repo.get("archived", False),
    }


def fetch_github_repositories(request_url):
    """请求 GitHub Search API，并处理常见错误。"""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-deepseek-analyzer",
    }

    try:
        response = requests.get(request_url, headers=headers, timeout=30)
    except requests.RequestException as error:
        print("请求 GitHub API 失败。")
        print(f"错误原因：{error}")
        return None, None

    print(f"HTTP 状态码：{response.status_code}")

    if response.status_code != 200:
        print("GitHub API 返回了错误。")
        print(f"错误信息：{response.text}")

        if response.status_code in (403, 429):
            print("可能触发了 GitHub 限流，请稍后再试。")

        return None, response.status_code

    try:
        return response.json(), response.status_code
    except json.JSONDecodeError as error:
        print("GitHub 返回内容不是合法 JSON。")
        print(f"解析失败原因：{error}")
        return None, response.status_code


def save_search_results(search_data, extracted_repos, request_url):
    """把搜索结果保存成 JSON 文件，方便后续脚本继续读取。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_data = {
        "request_url": request_url,
        "total_count": search_data.get("total_count", 0),
        "saved_count": len(extracted_repos),
        "items": extracted_repos,
    }

    with open(SEARCH_RESULTS_PATH, "w", encoding="utf-8") as file:
        json.dump(output_data, file, ensure_ascii=False, indent=2)

    return output_data


def search_github_repos(keyword, language, min_stars, top_k):
    """完整执行一次 GitHub 搜索，并保存搜索结果。"""
    if not keyword:
        print("请求失败：请提供 --keyword 参数")
        return None

    request_url = build_request_url(keyword, language, min_stars, top_k)

    print("实际请求 URL：")
    print(request_url)

    search_data, _status_code = fetch_github_repositories(request_url)

    if search_data is None:
        print("本次没有生成搜索结果文件。")
        return None

    total_count = search_data.get("total_count", 0)
    repo_items = search_data.get("items", [])
    extracted_repos = [extract_repo_info(repo) for repo in repo_items]

    output_data = save_search_results(search_data, extracted_repos, request_url)

    print(f"一共搜索到多少项目 total_count：{total_count}")
    print(f"本次保存了多少个项目：{len(extracted_repos)}")
    print(f"保存路径：{SEARCH_RESULTS_PATH}")

    print("本次保存的项目：")
    for repo in extracted_repos:
        print(f"- {repo['full_name']}，stars：{repo['stargazers_count']}")

    return output_data


def parse_args():
    """读取命令行参数。"""
    parser = argparse.ArgumentParser(description="搜索 GitHub 项目并保存为 JSON。")
    parser.add_argument("--keyword", default=None, help="搜索关键词")
    parser.add_argument("--language", default=None, help="编程语言")
    parser.add_argument("--min_stars", type=int, default=None, help="最低星标数")
    parser.add_argument("--top_k", type=int, default=None, help="返回项目数量")
    return parser.parse_args()


def ask_text(prompt_text, default_value=None):
    """向用户提问，读取一段文本。"""
    if default_value is None:
        user_input = input(f"{prompt_text}：").strip()
    else:
        user_input = input(f"{prompt_text}（默认 {default_value}）：").strip()

    if user_input:
        return user_input

    return default_value


def ask_required_text(prompt_text):
    """向用户提问，直到用户输入必填文本。"""
    while True:
        user_input = ask_text(prompt_text)

        if user_input:
            return user_input

        print("这个参数不能为空，请重新输入。")


def ask_int(prompt_text, default_value):
    """向用户提问，读取一个整数。"""
    while True:
        user_input = input(f"{prompt_text}（默认 {default_value}）：").strip()

        if not user_input:
            return default_value

        try:
            return int(user_input)
        except ValueError:
            print("请输入数字，例如：500、1000、10。")


def fill_missing_args(args):
    """命令行没传的参数，就在运行时一步步提示用户输入。"""
    has_cli_args = len(sys.argv) > 1

    if args.keyword is None:
        args.keyword = ask_required_text("请输入 keyword")

    if args.language is None:
        if has_cli_args:
            args.language = "Python"
        else:
            args.language = ask_text("请输入 language", "Python")

    if args.min_stars is None:
        if has_cli_args:
            args.min_stars = 500
        else:
            args.min_stars = ask_int("请输入 min_stars", 500)

    if args.top_k is None:
        if has_cli_args:
            args.top_k = 5
        else:
            args.top_k = ask_int("请输入 top_k", 5)

    return args


def main():
    args = parse_args()
    args = fill_missing_args(args)
    search_github_repos(args.keyword, args.language, args.min_stars, args.top_k)


if __name__ == "__main__":
    main()
