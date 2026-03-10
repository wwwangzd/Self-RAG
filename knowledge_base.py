"""知识库导入服务"""

import hashlib
import os
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter

import config_data as config
from vector_store import build_vector_store


def ensure_parent_directory(file_path: str):
    parent_directory = os.path.dirname(file_path)
    if parent_directory:
        os.makedirs(parent_directory, exist_ok=True)


def check_md5(md5_str: str, md5_path: str):
    ensure_parent_directory(md5_path)
    if not os.path.exists(md5_path):
        open(md5_path, "w", encoding="utf-8").close()
        return False

    with open(md5_path, "r", encoding="utf-8") as file:
        for line in file.readlines():
            if line.strip() == md5_str:
                return True
    return False


def save_md5(md5_str: str, md5_path: str):
    ensure_parent_directory(md5_path)
    with open(md5_path, "a", encoding="utf-8") as file:
        file.write(md5_str + "\n")


def get_string_md5(input_str: str, encoding="utf-8"):
    encoded_value = input_str.encode(encoding=encoding)
    md5_str = hashlib.md5(encoded_value).hexdigest()
    return md5_str


class KnowledgeBaseService(object):
    def __init__(self, knowledge_base_name=None):
        self.knowledge_base_name, self.knowledge_base_config, self.chroma = build_vector_store(knowledge_base_name)
        self.md5_path = self.knowledge_base_config["md5_path"]
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len,
        )

    def upload_by_str(self, data, filename, source_path=None, file_type=None):
        clean_data = data.strip()
        if not clean_data:
            print(f"跳过空内容文件：{filename}")
            return False

        md5_str = get_string_md5(clean_data, encoding="utf-8")

        if check_md5(md5_str, self.md5_path):
            print(f"内容重复，已跳过：{filename}")
            return False

        if len(clean_data) > config.max_split_char_num:
            chunks = self.splitter.split_text(clean_data)
        else:
            chunks = [clean_data]

        metadata = {
            "source": filename,
            "knowledge_base": self.knowledge_base_name,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        if source_path:
            metadata["source_path"] = source_path
        if file_type:
            metadata["file_type"] = file_type

        self.chroma.add_texts(
            chunks,
            metadatas=[metadata for _ in chunks],
        )

        save_md5(md5_str, self.md5_path)

        print(f"内容成功导入：{filename} -> {self.knowledge_base_name}")
        return True


if __name__ == "__main__":
    service = KnowledgeBaseService()
    service.upload_by_str("你好", "testfile")
