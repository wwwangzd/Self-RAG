"""RAG服务"""

from langchain_community.chat_models import ChatTongyi
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda

import config_data as config
from file_history_store import get_history
from knowledge_base_registry import build_session_config, normalize_knowledge_base_name
from vector_store import VectorStoreService


class RAGService(object):
    def __init__(self, knowledge_base_name=None, session_id=None):
        self.knowledge_base_name = normalize_knowledge_base_name(knowledge_base_name)
        self.session_id = session_id or config.default_session_id
        self.vector_service = VectorStoreService(self.knowledge_base_name)
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的参考资料为主，简洁专业地回答问题。\n参考资料：\n{context}"),
                ("system", "并且我提供用户历史对话记录如下：\n"),
                MessagesPlaceholder("history"),
                ("user", "请回答用户问题：{input}")
            ]
        )
        self.chat_model = ChatTongyi(model=config.chat_model_name, streaming=True)
        self.session_config = build_session_config(self.session_id, self.knowledge_base_name)
        self.chain = self.__get_chain()

    def __get_chain(self):
        retriever = self.vector_service.get_retriever()

        def format_retriever(value: dict):
            return value["input"]

        def format_func(docs: list[Document]):
            if not docs:
                return "无参考资料"

            format_str = ""
            for doc in docs:
                format_str += f"文档片段：{doc.page_content}\n文档元数据：{doc.metadata}\n\n"
            return format_str

        def format_prompt(value):
            new_value = {}
            new_value["input"] = value["input"]["input"]
            new_value["context"] = value["context"]
            new_value["history"] = value["input"]["history"]
            return new_value

        chain = (
                {
                    "input": RunnablePassthrough(),
                    "context": RunnableLambda(format_retriever) | retriever | RunnableLambda(format_func),
                } | RunnableLambda(format_prompt) | self.prompt_template | self.chat_model | StrOutputParser()
        )

        conv_chain = RunnableWithMessageHistory(
            chain, get_history, input_messages_key="input", history_messages_key="history"
        )

        return conv_chain


if __name__ == "__main__":
    rag_service = RAGService()
    ret = rag_service.chain.invoke({"input": "我之前问了你几次，问了什么"}, rag_service.session_config)
    print(ret)
