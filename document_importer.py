"""知识库导入辅助模块"""

from pathlib import Path

import config_data as config
from knowledge_base import KnowledgeBaseService
from knowledge_base_registry import (
    add_knowledge_base,
    get_knowledge_base_config,
    get_knowledge_base_names,
    has_knowledge_base,
    normalize_knowledge_base_name,
)


def list_knowledge_bases():
    knowledge_bases = []
    for knowledge_base_name in get_knowledge_base_names():
        knowledge_base_config = get_knowledge_base_config(knowledge_base_name)
        knowledge_bases.append(
            {
                "name": knowledge_base_name,
                "label": knowledge_base_config["label"],
                "collection_name": knowledge_base_config["collection_name"],
                "persist_directory": knowledge_base_config["persist_directory"],
            }
        )
    return knowledge_bases


def ensure_knowledge_base(knowledge_base_name, create_if_missing=False, label=None):
    normalized_name = normalize_knowledge_base_name(knowledge_base_name)
    if has_knowledge_base(normalized_name):
        return normalized_name, False

    if not create_if_missing:
        raise ValueError(
            f"知识库不存在：{normalized_name}。可先使用 --list-knowledge-bases 查看，"
            f"或配合 --create-knowledge-base 新建。"
        )

    add_knowledge_base(normalized_name, label=label)
    return normalized_name, True


def is_supported_file(file_path: Path):
    return file_path.suffix.lower() in config.SUPPORTED_FILE_EXTENSIONS


def collect_input_files(input_path, recursive=True):
    path = Path(input_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"路径不存在：{path}")

    if path.is_file():
        if not is_supported_file(path):
            raise ValueError(f"暂不支持的文件类型：{path.suffix}")
        return [path]

    if not path.is_dir():
        raise ValueError(f"无法处理的路径类型：{path}")

    pattern = "**/*" if recursive else "*"
    file_paths = [file_path for file_path in path.glob(pattern) if file_path.is_file() and is_supported_file(file_path)]
    return sorted(file_paths)


def read_text_file(file_path: Path):
    for encoding in config.TEXT_FILE_ENCODINGS:
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return file_path.read_text(encoding="utf-8", errors="ignore")


def read_pdf_file(file_path: Path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError("导入 PDF 前请先安装 pypdf：pip install pypdf") from exc

    reader = PdfReader(str(file_path))
    page_text_list = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            page_text_list.append(page_text)

    pdf_content = "\n".join(page_text_list).strip()
    if not pdf_content:
        raise ValueError(f"PDF 未提取到可用文本：{file_path}")
    return pdf_content


def read_document(file_path):
    path = Path(file_path).expanduser().resolve()
    suffix = path.suffix.lower()

    if suffix in config.TEXT_FILE_EXTENSIONS:
        content = read_text_file(path)
    elif suffix in config.PDF_FILE_EXTENSIONS:
        content = read_pdf_file(path)
    else:
        raise ValueError(f"暂不支持的文件类型：{suffix}")

    return {
        "content": content,
        "source_name": path.name,
        "source_path": str(path),
        "file_type": suffix,
    }


def import_documents(input_path, knowledge_base_name, recursive=True):
    service = KnowledgeBaseService(knowledge_base_name)
    file_paths = collect_input_files(input_path, recursive=recursive)

    if not file_paths:
        return {
            "success_count": 0,
            "skipped_count": 0,
            "failed_count": 0,
            "knowledge_base_name": knowledge_base_name,
            "errors": [],
        }

    success_count = 0
    skipped_count = 0
    failed_count = 0
    errors = []

    for file_path in file_paths:
        try:
            document = read_document(file_path)
            is_imported = service.upload_by_str(
                document["content"],
                document["source_name"],
                source_path=document["source_path"],
                file_type=document["file_type"],
            )
            if is_imported:
                success_count += 1
            else:
                skipped_count += 1
        except Exception as exc:
            failed_count += 1
            errors.append({"file_path": str(file_path), "reason": str(exc)})

    return {
        "success_count": success_count,
        "skipped_count": skipped_count,
        "failed_count": failed_count,
        "knowledge_base_name": knowledge_base_name,
        "errors": errors,
    }