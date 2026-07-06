import argparse
import sys

from analyze_repo import run_analysis
from search_github import SEARCH_RESULTS_PATH, search_github_repos


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args():
    """统一入口的命令行参数。"""
    parser = argparse.ArgumentParser(
        description="GitHub 项目学习推荐工具：搜索项目、调用 DeepSeek 分析、生成排名报告。"
    )
    parser.add_argument("--keyword", default=None, help="搜索关键词")
    parser.add_argument("--language", default=None, help="编程语言")
    parser.add_argument("--min_stars", type=int, default=None, help="最低星标数")
    parser.add_argument("--top_k", type=int, default=None, help="搜索并分析的项目数量")
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


def print_top_recommendations(ranked_results):
    """打印 Top 3 推荐项目，方便命令行快速查看。"""
    print("Top 3 推荐项目：")

    if not ranked_results:
        print("- 暂无成功分析的项目")
        return

    for index, result in enumerate(ranked_results[:3], start=1):
        print(
            f"{index}. {result['full_name']} "
            f"- final_score: {result['final_score']} "
            f"- {result['final_recommendation']}"
        )


def main():
    args = parse_args()
    args = fill_missing_args(args)

    print("开始搜索 GitHub 项目")
    print(f"搜索关键词：{args.keyword}")
    print(f"编程语言：{args.language}")
    print(f"最低星标数：{args.min_stars}")
    print(f"返回项目数量：{args.top_k}")

    search_data = search_github_repos(
        keyword=args.keyword,
        language=args.language,
        min_stars=args.min_stars,
        top_k=args.top_k,
    )

    if search_data is None:
        print("搜索失败，停止后续分析。")
        return

    print("开始调用 DeepSeek 分析项目")
    ranked_results, failed_results = run_analysis(
        input_path=SEARCH_RESULTS_PATH,
        top_k=args.top_k,
    )

    print("CLI 汇总")
    print(f"搜索关键词：{args.keyword}")
    print(f"返回项目数量：{search_data['saved_count']}")
    print(f"搜索到多少项目：{search_data['total_count']}")
    print(f"实际分析多少项目：{len(ranked_results) + len(failed_results)}")
    print(f"成功数量：{len(ranked_results)}")
    print(f"失败数量：{len(failed_results)}")
    print_top_recommendations(ranked_results)


if __name__ == "__main__":
    main()
