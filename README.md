# GitHub AI Project Analyzer

一句话简介：这是一个用 GitHub API 搜索开源项目，再用 DeepSeek 自动分析学习价值，并生成推荐排名的 AI 工具。

## 项目背景

GitHub 上有大量 AI Agent、RAG、LLM 应用项目。对初学者来说，真正困难的不是“找不到项目”，而是：

- 项目太多，不知道先看哪个；
- 星标高不一定适合学习；
- issue 太多可能说明项目复杂度较高；
- README、项目简介、学习路径需要人工反复判断；
- 初学者容易把时间花在不适合当前阶段的项目上。

这个工具想解决的问题是：

> 输入一个关键词，让程序自动搜索 GitHub 项目，再让 AI 帮你分析哪个项目更适合学习。

它不是为了替代人的判断，而是先帮你完成第一轮筛选，把“海量项目”变成“可比较的推荐列表”。

## 核心功能

- GitHub 项目搜索  
  使用 GitHub Search API，根据关键词、语言、最低星标数、返回数量搜索真实开源项目。

- AI 自动分析（DeepSeek）  
  调用 DeepSeek API，对项目简介、星标、issue 数等信息生成学习建议。

- 学习价值评分  
  结合项目元数据和 AI 分析结果，计算 `metadata_score`、`ai_learning_score`、`final_score`。

- 项目排序推荐  
  按 `final_score` 排名，生成 Top 推荐项目和 Markdown 报告。

- 双模式 CLI  
  既支持一次性传入参数，也支持直接运行后一步步输入参数。

## 系统架构说明

```text
GitHub API
    ↓
Python CLI
    ↓
DeepSeek API
    ↓
JSON 解析与字段校验
    ↓
Ranking 评分排序
    ↓
Markdown 推荐报告
```

更简化地说：

```text
GitHub API → Python → DeepSeek → JSON → Ranking
```

## 安装方式

### 1. 克隆项目

```bash
git clone https://github.com/Jeygen-JJ/github-deepseek-analyzer.git
cd github-deepseek-analyzer
```

### 2. 安装 Python 依赖

当前项目主要依赖 `requests`。

```bash
pip install -r requirements.txt
```

如果你暂时没有 `requirements.txt`，也可以手动安装：

```bash
pip install requests
```

### 3. 配置 DeepSeek API Key

当前代码读取的密钥文件是：

```text
env.env
```

可以先复制示例文件：

```bash
copy env.env.example env.env
```

也可以手动在项目根目录下创建 `env.env`：

```text
DEEPSEEK_API_KEY=你的DeepSeek API Key
```

注意：

- 不要把真实 API Key 提交到 GitHub。
- 当前仓库的 `.gitignore` 已经忽略 `env.env`。
- `env.env` 在这个项目里承担的就是常见 `.env` 配置文件的作用。
- 如果你习惯使用文件名 `.env`，需要同步修改 `llm_client.py` 里的 `ENV_FILE_PATH`；当前真实代码默认读取 `env.env`。

## 运行方式

### 方式一：一次性传入参数

```bash
python main.py --keyword "ai agent" --min_stars 500 --top_k 5
```

也可以指定语言：

```bash
python main.py --keyword "rag" --language Python --min_stars 1000 --top_k 10
```

参数含义：

- `--keyword`：搜索关键词，例如 `"ai agent"`、`"rag"`、`"llm app"`
- `--language`：编程语言，默认 `Python`
- `--min_stars`：最低星标数，默认 `500`
- `--top_k`：搜索并分析的项目数量，默认 `5`

### 方式二：交互式输入

如果你不想记命令行参数，可以直接运行：

```bash
python main.py
```

程序会依次提示：

```text
请输入 keyword：
请输入 language（默认 Python）：
请输入 min_stars（默认 500）：
请输入 top_k（默认 5）：
```

例如：

```text
请输入 keyword：ai agent
请输入 language（默认 Python）：直接回车
请输入 min_stars（默认 500）：1000
请输入 top_k（默认 5）：5
```

## 输出示例

命令行会输出类似内容：

```text
CLI 汇总
搜索关键词：ai agent
返回项目数量：5
搜索到多少项目：373
实际分析多少项目：5
成功数量：5
失败数量：0
Top 3 推荐项目：
1. Shubhamsaboo/awesome-llm-apps - final_score: 79.0 - 可以学习
2. langchain-ai/langchain - final_score: 79.0 - 可以学习
3. browser-use/browser-use - final_score: 73.0 - 可以学习
```

生成的文件：

```text
data/search_results.json
outputs/analysis_results.json
outputs/ranked_projects.md
```

其中：

- `data/search_results.json`：GitHub 搜索结果；
- `outputs/analysis_results.json`：AI 分析后的完整结构化结果；
- `outputs/ranked_projects.md`：适合人阅读的 Markdown 推荐报告。

## 当前限制

- 依赖 GitHub API：GitHub API 不可用时，无法搜索真实项目。
- 依赖 DeepSeek API：DeepSeek API Key 无效、额度不足或接口不可用时，无法完成 AI 分析。
- 依赖网络：搜索 GitHub 和调用 DeepSeek 都需要网络连接。
- 可能遇到 GitHub 限流：未配置 GitHub Token 时，GitHub Search API 有请求频率限制。
- 当前没有自动抓取 README 全文：在线搜索版本主要基于 GitHub 搜索结果中的项目元数据进行分析。
- 当前评分规则是学习辅助规则，不代表项目真实质量、商业价值或安全性。
- AI 输出可能偶尔不稳定：程序已做 JSON 解析和字段校验，但仍可能出现单个项目分析失败。

## 下一步计划

- 支持读取 GitHub README 内容，让 AI 分析更充分。
- 支持可选 GitHub Token，降低 API 限流概率。
- 增加缓存，避免重复调用 DeepSeek。
- 增加 `.env` 标准配置支持。
- 把评分规则抽成配置文件，方便用户调整权重。
- 增加更清晰的错误报告和运行日志。
- 增加单元测试，让项目更适合公开维护。
