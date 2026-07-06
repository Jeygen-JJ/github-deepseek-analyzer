# 项目复盘

## 已完成的功能

- 读取本地 `sample_repos.json`
- 批量分析多个 GitHub 项目
- 使用 `requests` 调用本地 Ollama
- 使用模型 `qwen2.5:1.5b`
- 要求 AI 输出 JSON
- 解析 AI 返回内容
- 支持处理带 Markdown JSON 代码块的返回
- 支持处理前后带解释文字的 JSON 返回
- 校验 AI 返回字段完整性
- 将成功结果放入 `results`
- 将失败结果放入 `failed_results`
- 计算 `metadata_score`
- 计算 `ai_learning_score`
- 计算 `final_score`
- 按 `final_score` 生成学习推荐排名
- 输出完整 JSON 文件：`outputs/analysis_results.json`
- 输出 Markdown 推荐报告：`outputs/ranked_projects.md`

## 当前项目优点

### 1. 路线稳定

当前项目不依赖浏览器控制，不需要 AI 去点击网页，所以比 browser-use 自动操作路线更稳定。

### 2. 适合初学者理解

代码流程比较直：

```text
读取 JSON → 调用 Ollama → 解析 JSON → 校验字段 → 打分 → 排名 → 保存报告
```

每一步都能单独理解。

### 3. 有失败处理

如果某个项目解析失败或字段缺失，程序不会直接崩溃，而是放入 `failed_results`。

### 4. 输出既适合程序，也适合人

- `analysis_results.json` 适合程序继续处理
- `ranked_projects.md` 适合人阅读和做笔记

### 5. 保留了本地优先路线

项目使用本地 Ollama，不依赖 OpenAI。适合练习本地模型和 Python 工具链。

## 当前项目不足

### 1. 当前未实现 GitHub API 实时搜索

项目目前只读取本地 `sample_repos.json`，还不会自动搜索 GitHub 项目。

### 2. 当前未实现自动读取 README

`readme_text` 目前是样本文件里手动准备的文本，不是程序自动从 GitHub 获取的。

### 3. 小模型输出不稳定

Ollama 小模型有时会输出英文，或者把难度写成 `Medium`、`Intermediate`、`1` 等格式。

当前项目还没有做统一格式清洗。

### 4. 评分规则比较简单

当前评分适合学习用途，但不能代表项目真实质量。

比如 stars 多不一定适合新手，issue 少也不一定说明项目简单。

### 5. 没有命令行参数

当前输入文件、模型名称、输出路径都写在代码里。

如果要换文件或模型，需要改代码。

## 后续可以升级的方向

### 1. 接入 GitHub API

从手写 `sample_repos.json` 升级为自动搜索项目。

### 2. 自动获取 README

根据 `full_name` 自动请求 GitHub README API，并填充 `readme_text`。

### 3. 增加缓存

同一个项目不要每次都重新调用 Ollama，节省时间。

### 4. 标准化 AI 输出

把 `Medium`、`Intermediate`、`中等` 等统一成固定等级。

### 5. 支持命令行参数

例如：

```bash
python analyze_repo.py --input sample_repos.json --model qwen2.5:1.5b
```

当前未实现这个功能。

### 6. 增加更详细的错误报告

例如统计：

- 哪些项目 JSON 解析失败
- 哪些项目缺字段
- 哪些项目 Ollama 请求失败

### 7. 生成更漂亮的 Markdown 报告

可以加入：

- 推荐理由
- 风险等级
- 学习路径
- 适合 fork / 适合阅读 / 暂缓学习 等分类

## 适合作为小红书/Obsidian 笔记的标题

- 我用 Python + Ollama 做了一个 GitHub 项目学习推荐器
- 放弃浏览器自动化后，我把 AI Agent 学习路线改稳了
- 本地 Ollama 也能做项目分析：从 JSON 到 Markdown 报告
- Python 初学者练手项目：批量分析 GitHub 项目并生成推荐排名
- AI Agent 入门不一定要控制浏览器，先学会结构化分析
- 用 3 个 GitHub 项目练习 JSON、for 循环、批处理和 AI 分析
