import argparse
import json
import os
import sys
from pathlib import Path

from llm_client import ask_deepseek


PROJECT_DIR = Path(__file__).parent
SAMPLE_REPO_PATH = PROJECT_DIR / "sample_repo.json"
SAMPLE_REPOS_PATH = PROJECT_DIR / "sample_repos.json"
SEARCH_RESULTS_PATH = PROJECT_DIR / "data" / "search_results.json"
OUTPUTS_DIR = PROJECT_DIR / "outputs"
ANALYSIS_RESULTS_PATH = OUTPUTS_DIR / "analysis_results.json"
RANKED_PROJECTS_PATH = OUTPUTS_DIR / "ranked_projects.md"
REQUIRED_ANALYSIS_FIELDS = [
    "project_summary",
    "beginner_difficulty",
    "learning_value",
    "suggested_first_step",
    "risk_warning",
]


if hasattr(sys.stdout, "reconfigure"):
    # Windows 终端默认编码可能不是 UTF-8，中文输出容易乱码。
    sys.stdout.reconfigure(encoding="utf-8")


def load_sample_repo():
    """读取本地 sample_repo.json，不访问 GitHub 网络接口。"""
    with SAMPLE_REPO_PATH.open("r", encoding="utf-8") as repo_file:
        return json.load(repo_file)


def load_sample_repos():
    """读取本地 sample_repos.json，得到多个项目组成的列表。"""
    with SAMPLE_REPOS_PATH.open("r", encoding="utf-8") as repos_file:
        return json.load(repos_file)


def load_repos_from_file(input_path):
    """从指定 JSON 文件读取项目列表。"""
    with Path(input_path).open("r", encoding="utf-8") as repos_file:
        data = json.load(repos_file)

    # search_results.json 是一个字典，项目列表放在 items 里面。
    if isinstance(data, dict):
        return data.get("items", [])

    # sample_repos.json 本身就是一个列表。
    if isinstance(data, list):
        return data

    return []


def normalize_repo_for_analysis(repo):
    """把不同来源的项目数据统一成分析函数需要的格式。"""
    description = repo.get("description") or "暂无项目简介"
    readme_text = repo.get("readme_text")

    if not readme_text:
        readme_text = (
            "当前数据来自 GitHub 搜索结果，暂未读取 README。"
            f"项目简介：{description}"
        )

    return {
        "full_name": repo.get("full_name", "未知项目"),
        "description": description,
        "stars": repo.get("stars", repo.get("stargazers_count", 0)),
        "open_issues": repo.get("open_issues", repo.get("open_issues_count", 0)),
        "readme_text": readme_text,
    }


def prepare_repos_for_analysis(repos, top_k=None):
    """控制实际分析数量，并统一字段格式。"""
    if top_k is not None:
        repos = repos[:top_k]

    return [normalize_repo_for_analysis(repo) for repo in repos]


def build_analysis_prompt(repo_data):
    """把项目数据拼成中文提示词，交给 DeepSeek 分析。"""
    return f"""
你是一个帮助 Python 初学者学习开源项目的助手。

请只输出 JSON，不要输出 Markdown，不要输出额外解释。
JSON 必须包含以下字段：
- project_summary
- beginner_difficulty
- learning_value
- suggested_first_step
- risk_warning

请根据下面这个 GitHub 项目信息，判断它是否适合初学者学习：

项目名称：{repo_data["full_name"]}
项目简介：{repo_data["description"]}
星标数：{repo_data["stars"]}
未关闭 issue 数：{repo_data["open_issues"]}
README 文本：
{repo_data["readme_text"]}
""".strip()


def parse_ai_json(text):
    """尽量把 AI 返回的文本解析成 Python 字典。"""
    try:
        # 第一种情况：模型返回的文本本身就是合法 JSON。
        return json.loads(text)
    except json.JSONDecodeError as error:
        print(f"直接解析 JSON 失败：{error}")

    if "```json" in text:
        try:
            # 第二种情况：模型把 JSON 包在 ```json 代码块里。
            json_block_start = text.index("```json") + len("```json")
            json_block_end = text.index("```", json_block_start)
            json_text = text[json_block_start:json_block_end].strip()
            return json.loads(json_text)
        except (ValueError, json.JSONDecodeError) as error:
            print(f"解析 ```json 代码块失败：{error}")

    try:
        # 第三种情况：模型前后有解释文字，中间才是真正的 JSON。
        json_start = text.index("{")
        json_end = text.rindex("}") + 1
        json_text = text[json_start:json_end]
        return json.loads(json_text)
    except (ValueError, json.JSONDecodeError) as error:
        print(f"提取大括号中的 JSON 失败：{error}")

    return None


def validate_analysis(data):
    """检查 AI 返回的 JSON 是否包含我们需要的字段。"""
    if not isinstance(data, dict):
        return REQUIRED_ANALYSIS_FIELDS

    missing_fields = []
    for field_name in REQUIRED_ANALYSIS_FIELDS:
        if field_name not in data:
            missing_fields.append(field_name)

    return missing_fields


def print_analysis_fields(analysis_data):
    """按固定顺序逐项打印解析后的分析结果。"""
    print("解析后的分析结果：")
    for field_name in REQUIRED_ANALYSIS_FIELDS:
        print(f"{field_name}: {analysis_data[field_name]}")


def analyze_one_repo(repo):
    """分析单个项目，成功和失败都返回清晰的数据。"""
    prompt = build_analysis_prompt(repo)
    model_result = ask_deepseek(prompt)

    print(f"正在分析：{repo['full_name']}")
    print("DeepSeek 原始返回内容：")
    print(model_result)

    if model_result.startswith("请求失败："):
        return {
            "success": False,
            "full_name": repo["full_name"],
            "error": "DeepSeek调用失败",
            "raw_response": model_result,
        }

    analysis_data = parse_ai_json(model_result)
    if analysis_data is None:
        return {
            "success": False,
            "full_name": repo["full_name"],
            "error": "JSON解析失败",
            "raw_response": model_result,
        }

    missing_fields = validate_analysis(analysis_data)
    if missing_fields:
        return {
            "success": False,
            "full_name": repo["full_name"],
            "error": "字段不完整",
            "missing_fields": missing_fields,
            "raw_response": model_result,
        }

    return {
        "success": True,
        "full_name": repo["full_name"],
        "description": repo["description"],
        "stars": repo["stars"],
        "open_issues": repo["open_issues"],
        "project_summary": analysis_data["project_summary"],
        "beginner_difficulty": analysis_data["beginner_difficulty"],
        "learning_value": analysis_data["learning_value"],
        "suggested_first_step": analysis_data["suggested_first_step"],
        "risk_warning": analysis_data["risk_warning"],
    }


def analyze_repos(repos):
    """批量分析项目：成功放入 results，失败放入 failed_results。"""
    results = []
    failed_results = []

    for repo in repos:
        analysis_result = analyze_one_repo(repo)
        if analysis_result["success"]:
            results.append(analysis_result)
        else:
            failed_results.append(analysis_result)

    return results, failed_results


def calculate_metadata_score(repo):
    """根据项目元数据计算基础分：星标、issue、名称和简介。"""
    score = 0

    if repo["stars"] >= 10000:
        score += 40
    elif repo["stars"] >= 1000:
        score += 30
    else:
        score += 10

    if repo["open_issues"] <= 100:
        score += 40
    elif repo["open_issues"] <= 1000:
        score += 25
    else:
        score += 10

    if repo["full_name"] and repo["description"]:
        score += 20

    return score


def calculate_ai_learning_score(analysis):
    """根据 AI 分析内容计算学习适合度分。"""
    score = 0
    difficulty_text = analysis["beginner_difficulty"]
    risk_warning_text = analysis["risk_warning"]

    if "低" in difficulty_text or "简单" in difficulty_text:
        score += 35
    elif "中等" in difficulty_text:
        score += 25
    elif "高" in difficulty_text or "困难" in difficulty_text:
        score += 10

    if analysis["learning_value"]:
        score += 25

    if analysis["suggested_first_step"]:
        score += 25

    # 风险提示中出现这些词，说明初学者可能会遇到额外门槛。
    risk_keywords = ["API", "TOKEN", "复杂", "依赖"]
    if any(keyword in risk_warning_text.upper() for keyword in risk_keywords):
        score -= 10

    return max(0, min(score, 100))


def calculate_final_score(metadata_score, ai_learning_score):
    """把项目元数据分和 AI 学习分合并成最终分。"""
    return round(metadata_score * 0.4 + ai_learning_score * 0.6, 1)


def get_final_recommendation(final_score):
    """根据最终分给出学习推荐等级。"""
    if final_score >= 85:
        return "优先学习"
    if final_score >= 70:
        return "可以学习"
    if final_score >= 55:
        return "先收藏，暂缓学习"

    return "暂不推荐"


def add_scores_to_result(result):
    """给单个成功结果补充三个分数和最终推荐。"""
    metadata_score = calculate_metadata_score(result)
    ai_learning_score = calculate_ai_learning_score(result)
    final_score = calculate_final_score(metadata_score, ai_learning_score)

    result["metadata_score"] = metadata_score
    result["ai_learning_score"] = ai_learning_score
    result["final_score"] = final_score
    result["final_recommendation"] = get_final_recommendation(final_score)

    return result


def rank_projects(results):
    """先给项目打分，再按 final_score 从高到低排序。"""
    scored_results = []
    for result in results:
        scored_results.append(add_scores_to_result(result))

    return sorted(
        scored_results,
        key=lambda result: (-result["final_score"], result["open_issues"]),
    )


def save_results(results, failed_results):
    """把成功和失败结果保存到 outputs/analysis_results.json。"""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    output_data = {
        "results": results,
        "failed_results": failed_results,
    }

    with ANALYSIS_RESULTS_PATH.open("w", encoding="utf-8") as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=2)


def save_markdown_report(ranked_results, failed_results):
    """生成适合人阅读的 Markdown 推荐报告。"""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    markdown_lines = [
        "# GitHub 项目学习推荐排名",
        "",
        "## 汇总",
        "",
        f"- 分析项目数：{len(ranked_results) + len(failed_results)}",
        f"- 成功数：{len(ranked_results)}",
        f"- 失败数：{len(failed_results)}",
        "",
        "## 排名表格",
        "",
        "| 排名 | 项目名 | stars | open_issues | beginner_difficulty | metadata_score | ai_learning_score | final_score | final_recommendation |",
        "| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | --- |",
    ]

    for index, result in enumerate(ranked_results, start=1):
        markdown_lines.append(
            "| "
            f"{index} | "
            f"{result['full_name']} | "
            f"{result['stars']} | "
            f"{result['open_issues']} | "
            f"{result['beginner_difficulty']} | "
            f"{result['metadata_score']} | "
            f"{result['ai_learning_score']} | "
            f"{result['final_score']} | "
            f"{result['final_recommendation']} |"
        )

    markdown_lines.extend(["", "## 详细学习建议", ""])

    for index, result in enumerate(ranked_results, start=1):
        markdown_lines.extend(
            [
                f"### {index}. {result['full_name']}",
                "",
                f"- 项目总结：{result['project_summary']}",
                f"- 学习价值：{result['learning_value']}",
                f"- 建议第一步：{result['suggested_first_step']}",
                f"- 风险提醒：{result['risk_warning']}",
                "",
            ]
        )

    if failed_results:
        markdown_lines.extend(["## 失败项目", ""])
        for failed_result in failed_results:
            markdown_lines.append(f"- {failed_result['full_name']}：{failed_result['error']}")

    with RANKED_PROJECTS_PATH.open("w", encoding="utf-8") as report_file:
        report_file.write("\n".join(markdown_lines) + "\n")


def print_batch_summary(total_count, results, failed_results):
    """打印批量分析摘要，方便在命令行快速查看。"""
    print("批量分析完成")
    print(f"一共分析了 {total_count} 个项目")
    print(f"成功 {len(results)} 个")
    print(f"失败 {len(failed_results)} 个")

    if results:
        print(f"最终排名第一的项目：{results[0]['full_name']}")
        print(f"最终排名最后的项目：{results[-1]['full_name']}")

    for result in results:
        print(f"- {result['full_name']}")
        print(f"  beginner_difficulty: {result['beginner_difficulty']}")
        print(f"  suggested_first_step: {result['suggested_first_step']}")
        print(f"  final_score: {result['final_score']}")
        print(f"  final_recommendation: {result['final_recommendation']}")

    if failed_results:
        print("失败项目：")
        for failed_result in failed_results:
            print(f"- {failed_result['full_name']}：{failed_result['error']}")

    print(f"Markdown报告路径：{RANKED_PROJECTS_PATH}")


def run_analysis(input_path=SAMPLE_REPOS_PATH, top_k=None):
    """执行完整分析流程，方便 main.py 复用。"""
    raw_repos = load_repos_from_file(input_path)
    repos = prepare_repos_for_analysis(raw_repos, top_k)
    results, failed_results = analyze_repos(repos)
    ranked_results = rank_projects(results)
    save_results(ranked_results, failed_results)
    save_markdown_report(ranked_results, failed_results)
    print_batch_summary(len(repos), ranked_results, failed_results)
    return ranked_results, failed_results


def parse_args():
    """读取命令行参数。"""
    parser = argparse.ArgumentParser(description="分析 GitHub 项目并生成推荐排名。")
    parser.add_argument(
        "--input",
        default=str(SAMPLE_REPOS_PATH),
        help="输入 JSON 文件路径，默认读取 sample_repos.json",
    )
    parser.add_argument("--top_k", type=int, default=None, help="实际分析项目数量")
    return parser.parse_args()


def main():
    args = parse_args()
    run_analysis(args.input, args.top_k)


def run_single_repo_demo():
    """保留单项目分析演示，方便之后对比学习。"""
    repo_data = load_sample_repo()
    prompt = build_analysis_prompt(repo_data)
    model_result = ask_deepseek(prompt)

    print("DeepSeek 原始返回内容：")
    print(model_result)

    analysis_data = parse_ai_json(model_result)
    if analysis_data is None:
        print("JSON解析失败")
        print("原始返回内容如下，方便排查：")
        print(model_result)
        return

    missing_fields = validate_analysis(analysis_data)
    if missing_fields:
        print("JSON解析成功，但字段不完整")
        print("缺少字段：")
        for field_name in missing_fields:
            print(f"- {field_name}")
        return

    print("JSON解析成功")
    print_analysis_fields(analysis_data)


if __name__ == "__main__":
    main()
