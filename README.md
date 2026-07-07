# GitHub AI Project Analyzer

帮你从海量 GitHub AI 项目里，快速找出最值得学习的项目，并给出分数和推荐理由。

## 示例输入输出

输入：

```text
keyword = ai agent
```

输出：

```text
Top 3 项目 + 分数 + 推荐理由
```

示例结果：

```text
1. Shubhamsaboo/awesome-llm-apps
   final_score: 79.0
   推荐：可以学习
   理由：示例丰富，适合从具体项目入手，但部分示例可能需要 API Key。

2. langchain-ai/langchain
   final_score: 79.0
   推荐：可以学习
   理由：生态成熟，学习价值高，但项目较大，建议只从一个小示例开始。

3. browser-use/browser-use
   final_score: 73.0
   推荐：可以学习
   理由：适合了解 AI Agent 如何操作浏览器，但对初学者有一定复杂度。
```

## 这个工具是做什么的

你输入一个关键词，比如：

```text
ai agent
```

它会自动做三件事：

1. 去 GitHub 搜索相关项目；
2. 让 DeepSeek 分析这些项目是否适合学习；
3. 输出一个带分数和推荐理由的项目排名。

简单说，它像一个“GitHub 项目学习顾问”。

## 为什么要做这个工具

很多人想学 AI，但第一步就卡住了：

> GitHub 上项目太多，我到底该看哪个？

星标高的项目，不一定适合初学者。  
看起来很火的项目，可能 issue 很多、依赖复杂、文档难读。  
一个个点进去看 README，又很耗时间。

这个工具的目标不是替你做最终决定，而是帮你先完成第一轮筛选：

```text
从“我不知道看哪个”
变成“我知道可以先看这 3 个”
```

## 真实使用场景

### 场景 1：我想学 AI Agent，但不知道从哪个项目开始

你可以运行：

```bash
python main.py --keyword "ai agent" --min_stars 500 --top_k 5
```

工具会返回几个相关项目，并告诉你：

- 哪个更适合先看；
- 哪个可能太复杂；
- 哪个适合收藏但不急着 fork；
- 第一步可以从哪里开始。

### 场景 2：我想找最值得学的 GitHub 项目

你可以换关键词：

```bash
python main.py --keyword "rag" --min_stars 1000 --top_k 10
```

然后看输出报告里的排名和推荐理由。

### 场景 3：我想做 AI 学习笔记或项目选题

运行后打开：

```text
outputs/ranked_projects.md
```

这里会生成一份 Markdown 报告，适合放进 Obsidian、Notion 或学习日志里。

## 效果对比

| 没用这个工具 | 用这个工具 |
| --- | --- |
| 手动在 GitHub 搜索很多项目 | 输入关键词自动搜索 |
| 一个个点开项目看简介 | 自动整理项目关键信息 |
| 只看 stars 判断项目好坏 | 同时参考 stars、issue、AI 分析 |
| 不知道项目是否适合初学者 | 给出学习难度和推荐结论 |
| 看完还是不知道先学哪个 | 输出 Top 3 推荐项目 |
| 学习记录难整理 | 自动生成 Markdown 报告 |

## 输出解释

工具会输出一个 `final_score`。

你可以把它理解成：

> 这个项目对当前学习者的综合推荐分。

它不是简单看星标数，也不是说这个项目“绝对好”或“绝对不好”。

它会综合考虑：

- 项目是否有足够关注度；
- 未关闭 issue 是否太多；
- 项目信息是否完整；
- DeepSeek 判断的学习难度；
- DeepSeek 给出的学习价值；
- 是否有明确的第一步建议；
- 是否存在 API Key、依赖复杂、配置麻烦等风险。

推荐等级大致可以这样理解：

| final_score | 推荐结论 | 怎么理解 |
| ---: | --- | --- |
| 85 以上 | 优先学习 | 很适合作为当前阶段的练习项目 |
| 70 - 84 | 可以学习 | 值得看，但要选小入口开始 |
| 55 - 69 | 先收藏，暂缓学习 | 有价值，但当前可能偏难 |
| 55 以下 | 暂不推荐 | 不建议作为第一批学习对象 |

## 核心功能

- GitHub 项目搜索  
  根据关键词、语言、最低星标数、返回数量搜索真实 GitHub 项目。

- AI 自动分析  
  调用 DeepSeek 分析项目的学习价值、学习难度、第一步建议和风险提醒。

- 学习价值评分  
  生成 `metadata_score`、`ai_learning_score` 和 `final_score`。

- 项目排序推荐  
  根据最终分数生成推荐排名。

- Markdown 报告  
  自动生成适合阅读和收藏的项目推荐报告。

- 两种运行方式  
  支持一次性输入参数，也支持运行后一步步提示输入。

## 工作流程

```text
输入关键词
    ↓
搜索 GitHub 项目
    ↓
提取项目基本信息
    ↓
DeepSeek 分析学习价值
    ↓
Python 计算分数
    ↓
生成 Top 推荐项目
    ↓
输出 Markdown 报告
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

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 DeepSeek API Key

复制示例文件：

```bash
copy env.env.example env.env
```

然后在 `env.env` 里填写自己的 DeepSeek API Key：

```text
DEEPSEEK_API_KEY=你的DeepSeek API Key
```

注意：不要把真实 API Key 提交到 GitHub。

## 运行方式

### 方式一：一次性运行

```bash
python main.py --keyword "ai agent" --min_stars 500 --top_k 5
```

### 方式二：按提示输入

```bash
python main.py
```

程序会提示：

```text
请输入 keyword：
请输入 language（默认 Python）：
请输入 min_stars（默认 500）：
请输入 top_k（默认 5）：
```

## 输出文件

运行后会生成：

```text
data/search_results.json
outputs/analysis_results.json
outputs/ranked_projects.md
```

建议优先查看：

```text
outputs/ranked_projects.md
```

它是最适合人阅读的推荐报告。

## 当前限制

- 需要网络连接。
- 需要 DeepSeek API Key。
- GitHub API 可能会限流。
- 当前主要基于 GitHub 搜索结果中的项目信息分析，还没有自动读取完整 README。
- AI 分析结果可能会有轻微波动。
- 评分是学习辅助建议，不代表项目真实质量或商业价值。

## 下一步计划

- 自动读取项目 README，让分析更准确。
- 支持 GitHub Token，减少限流问题。
- 增加缓存，避免重复调用 DeepSeek。
- 增加更稳定的测试。
- 支持更漂亮的 HTML 报告。
