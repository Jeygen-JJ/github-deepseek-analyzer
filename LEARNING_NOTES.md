# 学习笔记

## 我在这个项目中学到了什么

这个项目把一个 AI 小工具拆成了几个容易理解的步骤：

1. 准备本地 JSON 数据
2. 用 Python 读取 JSON
3. 用 for 循环批量处理多个项目
4. 调用本地 Ollama 模型
5. 解析 AI 返回的 JSON
6. 校验字段是否完整
7. 区分成功结果和失败结果
8. 给项目打分
9. 按分数排序
10. 生成 JSON 和 Markdown 报告

它不是一个复杂产品，但很适合用来练习“AI 工具的基本数据流”。

## JSON 是什么

JSON 是一种常见的数据格式。

它长得像这样：

```json
{
  "full_name": "browser-use/browser-use",
  "stars": 101252,
  "open_issues": 281
}
```

你可以把 JSON 理解成“用文本保存的数据表”。它适合程序读取，也适合 API 返回数据。

## json.loads 是什么

`json.loads` 是 Python 标准库 `json` 里的函数。

它的作用是：把 JSON 字符串变成 Python 可以操作的数据。

例如：

```python
json.loads('{"name": "browser-use"}')
```

会变成 Python 字典：

```python
{"name": "browser-use"}
```

注意，“看起来像 JSON”不一定是合法 JSON。JSON 对双引号、逗号、大括号都有严格要求。

## 字段校验是什么

字段校验就是检查 AI 返回的数据里有没有我们需要的字段。

本项目要求 AI 返回：

- `project_summary`
- `beginner_difficulty`
- `learning_value`
- `suggested_first_step`
- `risk_warning`

如果缺少字段，后面的评分和报告生成就可能出错。所以程序会先检查字段是否完整。

## for 循环是什么

`for` 循环就是“一个一个处理”。

例如：

```python
for repo in repos:
    analyze_one_repo(repo)
```

意思是：从 `repos` 这个列表中，每次拿出一个项目，交给 `analyze_one_repo` 分析。

## 批处理是什么

批处理就是一次处理多个数据。

以前程序只分析一个项目，现在可以分析多个项目：

```text
browser-use/browser-use
langchain-ai/langchain
Shubhamsaboo/awesome-llm-apps
```

这就是从“单个项目分析”升级成“批量分析”。

## results 和 failed_results 为什么要分开

因为批量处理时，不应该让一个项目失败就影响所有项目。

所以程序分成两个列表：

- `results`：成功分析的项目
- `failed_results`：失败的项目

这样即使某个项目 JSON 解析失败，其他项目也能继续分析。

## metadata_score 是什么

`metadata_score` 是根据项目基础信息计算的分数。

它主要看：

- stars 是否足够多
- open_issues 是否较少
- full_name 和 description 是否完整

它反映的是“项目元数据看起来是否适合学习”。

## ai_learning_score 是什么

`ai_learning_score` 是根据 Ollama 的分析结果计算的分数。

它主要看：

- 初学者难度是否较低
- 学习价值是否存在
- 是否有建议第一步
- 风险提醒中是否出现 API、TOKEN、复杂、依赖等门槛

它反映的是“AI 认为这个项目是否适合学习”。

## final_score 是什么

`final_score` 是最终推荐分。

公式是：

```text
final_score = metadata_score * 0.4 + ai_learning_score * 0.6
```

意思是：

- 项目基础信息占 40%
- AI 学习分析占 60%

最终用它来生成学习推荐排名。

## 这个项目和 AI Agent 学习有什么关系

AI Agent 不只是“让 AI 控制浏览器”。

更基础的一条路线是：

```text
输入数据 → 构造任务 → 调用模型 → 解析输出 → 校验结果 → 生成行动建议
```

这个项目就在练这条路线。

它没有让 AI 自动点击网页，但它已经具备 AI Agent 工作流里的几个关键能力：

- 给模型明确任务
- 让模型输出结构化结果
- 用程序检查模型输出是否可靠
- 根据结果做下一步决策

这些能力比直接控制浏览器更稳定，也更适合初学阶段。
