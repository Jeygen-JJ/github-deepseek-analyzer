# 使用说明

这份文档说明如何安装、配置和运行 GitHub AI Project Analyzer。

## 如何安装

进入项目目录：

```bash
cd github-deepseek-analyzer
```

安装依赖：

```bash
pip install -r requirements.txt
```

如果没有使用 `requirements.txt`，也可以手动安装：

```bash
pip install requests
```

## 如何配置 DeepSeek API

当前项目使用 DeepSeek API 做项目分析。

在项目目录下创建：

```text
env.env
```

推荐先复制示例文件：

```bash
copy env.env.example env.env
```

写入：

```text
DEEPSEEK_API_KEY=你的DeepSeek API Key
```

注意：

- `env.env` 是本地密钥文件，不要提交到 GitHub。
- 当前 `.gitignore` 已经忽略 `env.env`。
- 程序不会在命令行打印你的 API Key。

## 如何运行 CLI

### 推荐方式：一次性传参

```bash
python main.py --keyword "ai agent" --min_stars 500 --top_k 5
```

指定语言：

```bash
python main.py --keyword "rag" --language Python --min_stars 1000 --top_k 10
```

### 初学者友好方式：交互式输入

直接运行：

```bash
python main.py
```

程序会提示你输入：

```text
请输入 keyword：
请输入 language（默认 Python）：
请输入 min_stars（默认 500）：
请输入 top_k（默认 5）：
```

如果你看到默认值，直接回车就会使用默认值。

## 参数说明

| 参数 | 示例 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--keyword` | `"ai agent"` | 无 | 搜索关键词。交互式运行时必须输入。 |
| `--language` | `Python` | `Python` | GitHub 项目主要语言。 |
| `--min_stars` | `500` | `500` | 只搜索星标数大于该值的项目。 |
| `--top_k` | `5` | `5` | 搜索并分析多少个项目。 |

## 输出结果在哪里

运行完成后主要看这三个文件：

```text
data/search_results.json
outputs/analysis_results.json
outputs/ranked_projects.md
```

建议先打开：

```text
outputs/ranked_projects.md
```

它是最适合人阅读的推荐报告。

## 常见错误

### 1. DeepSeek API 失败

可能表现：

```text
请求失败：DeepSeek API Key 无效或没有权限，请检查 env.env。
```

常见原因：

- `env.env` 不存在；
- `DEEPSEEK_API_KEY` 写错；
- API Key 已失效；
- DeepSeek 账号额度不足；
- 网络无法访问 DeepSeek API。

处理方式：

1. 确认 `env.env` 在当前项目目录下；
2. 确认内容格式是：

```text
DEEPSEEK_API_KEY=你的DeepSeek API Key
```

3. 不要在 key 前后多写空格；
4. 重新运行程序。

### 2. GitHub 限流

可能表现：

```text
GitHub API 返回了错误。
可能触发了 GitHub 限流，请稍后再试。
```

常见原因：

- 短时间内请求 GitHub API 太多；
- 当前版本没有使用 GitHub Token；
- 网络环境触发 GitHub 访问限制。

处理方式：

- 等一段时间再试；
- 减小 `--top_k`；
- 后续可以升级为支持 GitHub Token。

### 3. JSON 解析失败

可能表现：

```text
JSON解析失败
```

原因：

DeepSeek 理论上应该返回 JSON，但 AI 模型偶尔可能输出额外解释、格式错误或缺少字段。

当前程序已经尝试：

1. 直接解析 JSON；
2. 提取 Markdown JSON 代码块；
3. 提取第一个 `{` 到最后一个 `}` 之间的内容。

如果仍然失败，该项目会进入 `failed_results`，不会让整个程序崩溃。

### 4. 没有生成 Markdown 报告

先看命令行是否出现错误。

正常情况下，报告路径是：

```text
outputs/ranked_projects.md
```

如果没有生成，通常是：

- GitHub 搜索失败；
- DeepSeek 调用全部失败；
- 当前目录不对。

建议确认你是在这个目录运行：

```text
github-deepseek-analyzer
```
