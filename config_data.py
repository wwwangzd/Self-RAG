"""项目配置"""

import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 持久化文件路径
chat_history_directory = os.path.join(BASE_DIR, "chat_history") # 聊天记录持久化目录
VECTOR_STORE_DIRECTORY = os.path.join(BASE_DIR, "chroma_db") # 知识库向量库存储目录
MD5_DIRECTORY = os.path.join(BASE_DIR, "md5") # 知识库文件去重目录
KNOWLEDGE_BASE_REGISTRY_PATH = os.path.join(BASE_DIR, "knowledge_bases.json") # 知识库注册表文件

# 文件导入参数
SUPPORTED_FILE_EXTENSIONS = {".txt", ".pdf"} # 支持导入的文件后缀集合
TEXT_FILE_EXTENSIONS = {".txt"} # 文本文件后缀，用于选择文本读取逻辑
PDF_FILE_EXTENSIONS = {".pdf"} # PDF 文件后缀，用于选择 PDF 提取逻辑
TEXT_FILE_ENCODINGS = ("utf-8", "utf-8-sig", "gb18030", "gbk") # 文本文件的兜底编码顺序

# 知识库参数
DEFAULT_KNOWLEDGE_BASE = "default" # 默认知识库名称
DEFAULT_KNOWLEDGE_BASES = {
    "default": {"label": "默认知识库"},
    "notes": {"label": "个人笔记库"},
} # 注册表默认知识库
KNOWLEDGE_BASE_COLLECTION_PREFIX = "rag" # 新知识库名称前缀


# 检索参数
chunk_size = 1000 # 文本切分块大小
chunk_overlap = 100 # 相邻分块的重叠字符数
separators = ["\n\n", "\n", ".", "。", "!", "！", "?", "？", " ", ""] # 优先使用的分隔符顺序
max_split_char_num = 1000 # 超过该长度后再进行文本切分
similarity_threshold = 5 # 检索返回的候选文档数

# 模型参数
embedding_model_name = "text-embedding-v4"
chat_model_name = "qwen-flash"

# 默认会话编号
default_session_id = "user_001"