"""聊天历史服务"""

import json
import os
from typing import Sequence

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_to_dict, messages_from_dict

import config_data as config


class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id, storage_path):
        self.session_id = self._normalize_session_id(session_id)
        self.storage_path = storage_path
        self.file_path = os.path.join(self.storage_path, f"{self.session_id}.json")

        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    @staticmethod
    def _normalize_session_id(session_id):
        return session_id.replace(os.sep, "_").replace("..", "_")

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        all_messages = list(self.messages)
        all_messages.extend(messages)

        new_messages = messages_to_dict(all_messages)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f, ensure_ascii=False)

    @property
    def messages(self) -> Sequence[BaseMessage]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                messages_data = json.load(f)
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)


def get_history(session_id):
    return FileChatMessageHistory(session_id, config.chat_history_directory)
