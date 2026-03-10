# Self-RAG

一个基于命令行的个人知识库问答项目，支持多知识库导入和交互式问答。

## 功能

- 支持导入 `txt` 和 `pdf`
- 支持导入单文件或整个目录
- 支持创建和切换多个知识库
- 支持在命令行中基于指定知识库进行问答

## 环境准备

建议使用 Python 3.10+。

```bash
git clone <your-repo-url>
cd Self-RAG
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

如果你使用 conda，也可以自行创建环境后再安装依赖。

项目使用阿里云 DashScope 模型，请先配置环境变量：

```bash
export DASHSCOPE_API_KEY="your_api_key"
```

首次运行时，程序会自动创建运行时目录和 `knowledge_bases.json` 注册表。
这个注册表属于本地运行数据，默认不会提交到 Git。

## 导入知识库

运行导入程序：

```bash
python document_uploader.py
```

进入后可使用这些命令：

```text
/help
/list
/use notes
/create my_kb 我的知识库
/import ./docs
/import ./docs --non-recursive
/status
/exit
```

推荐流程：

```text
/list
/create project_docs 项目文档库
/use project_docs
/import ./docs
/exit
```

## 开始问答

运行问答程序：

```bash
python ask.py
```

进入后可使用这些命令：

```text
/help
/list
/use project_docs
/status
/exit
```

普通问题直接输入后按回车提交；命令必须以 `/` 开头。

## 目录说明

- `ask.py`: 命令行问答入口
- `document_uploader.py`: 命令行导入入口
- `knowledge_bases.json`: 知识库注册表，只保存可移植的知识库元信息
- `chroma_db/`, `md5/`, `chat_history/`: 运行时生成的数据目录，不应提交到仓库

## 许可证

本项目使用 MIT License，详见 [LICENSE](LICENSE)。