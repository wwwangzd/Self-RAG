"""知识库注册与会话配置服务"""

import json
import os
import re

import config_data as config


def normalize_knowledge_base_name(knowledge_base_name):
    if knowledge_base_name is None:
        return config.DEFAULT_KNOWLEDGE_BASE

    normalized_name = re.sub(r"[^0-9a-zA-Z_-]+", "_", knowledge_base_name.strip()).strip("_").lower()
    if not normalized_name:
        raise ValueError("知识库名称不能为空，且建议使用英文、数字、下划线或中划线。")
    return normalized_name


def _build_knowledge_base_config(knowledge_base_name, label=None):
    normalized_name = normalize_knowledge_base_name(knowledge_base_name)
    return {
        "label": label or normalized_name,
        "collection_name": f"{config.KNOWLEDGE_BASE_COLLECTION_PREFIX}_{normalized_name}",
        "persist_directory": os.path.join(config.VECTOR_STORE_DIRECTORY, normalized_name),
        "md5_path": os.path.join(config.MD5_DIRECTORY, f"{normalized_name}.txt"),
    }


def _build_default_knowledge_bases():
    knowledge_bases = {}
    for knowledge_base_name, knowledge_base_data in config.DEFAULT_KNOWLEDGE_BASES.items():
        knowledge_bases[knowledge_base_name] = _build_portable_knowledge_base_entry(
            knowledge_base_name,
            label=knowledge_base_data.get("label"),
        )
    return knowledge_bases


def _build_portable_knowledge_base_entry(knowledge_base_name, label=None):
    normalized_name = normalize_knowledge_base_name(knowledge_base_name)
    return {
        "label": label or normalized_name,
    }


def _ensure_registry_file():
    registry_path = config.KNOWLEDGE_BASE_REGISTRY_PATH
    if os.path.exists(registry_path):
        return

    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    with open(registry_path, "w", encoding="utf-8") as file:
        json.dump(_build_default_knowledge_bases(), file, ensure_ascii=False, indent=2)


def _load_knowledge_base_registry():
    _ensure_registry_file()
    with open(config.KNOWLEDGE_BASE_REGISTRY_PATH, "r", encoding="utf-8") as file:
        registry = json.load(file)

    normalized_registry = {}
    portable_registry = {}
    for knowledge_base_name, knowledge_base_config in registry.items():
        normalized_name = normalize_knowledge_base_name(knowledge_base_name)
        portable_registry[normalized_name] = _build_portable_knowledge_base_entry(
            normalized_name,
            label=knowledge_base_config.get("label"),
        )
        normalized_registry[normalized_name] = {
            **_build_knowledge_base_config(
                normalized_name,
                label=knowledge_base_config.get("label"),
            ),
            **portable_registry[normalized_name],
        }

    if registry != portable_registry:
        _save_knowledge_base_registry(portable_registry)

    return normalized_registry


def _save_knowledge_base_registry(knowledge_bases):
    with open(config.KNOWLEDGE_BASE_REGISTRY_PATH, "w", encoding="utf-8") as file:
        json.dump(knowledge_bases, file, ensure_ascii=False, indent=2)


def get_knowledge_base_names():
    return list(_load_knowledge_base_registry().keys())


def get_knowledge_base_config(knowledge_base_name=None):
    normalized_name = normalize_knowledge_base_name(knowledge_base_name)
    knowledge_bases = _load_knowledge_base_registry()
    if normalized_name not in knowledge_bases:
        raise ValueError(f"未配置知识库：{normalized_name}")
    return knowledge_bases[normalized_name]


def get_knowledge_base_label(knowledge_base_name):
    knowledge_base_config = get_knowledge_base_config(knowledge_base_name)
    return knowledge_base_config["label"]


def has_knowledge_base(knowledge_base_name):
    normalized_name = normalize_knowledge_base_name(knowledge_base_name)
    return normalized_name in _load_knowledge_base_registry()


def add_knowledge_base(knowledge_base_name, label=None, exist_ok=False):
    normalized_name = normalize_knowledge_base_name(knowledge_base_name)
    knowledge_bases = _load_knowledge_base_registry()

    if normalized_name in knowledge_bases:
        if not exist_ok:
            raise ValueError(f"知识库已存在：{normalized_name}")
        return normalized_name, knowledge_bases[normalized_name]

    knowledge_bases[normalized_name] = _build_knowledge_base_config(normalized_name, label=label)
    portable_knowledge_bases = {
        current_name: _build_portable_knowledge_base_entry(current_name, data.get("label"))
        for current_name, data in knowledge_bases.items()
    }
    _save_knowledge_base_registry(portable_knowledge_bases)
    return normalized_name, knowledge_bases[normalized_name]


def build_history_session_id(session_id=None, knowledge_base_name=None):
    current_session_id = session_id or config.default_session_id
    current_knowledge_base = normalize_knowledge_base_name(knowledge_base_name)
    return f"{current_knowledge_base}__{current_session_id}"


def build_session_config(session_id=None, knowledge_base_name=None):
    return {
        "configurable": {
            "session_id": build_history_session_id(session_id, knowledge_base_name),
        }
    }


session_config = build_session_config()