"""向量检索服务"""

from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

import config_data as config
from knowledge_base_registry import get_knowledge_base_config, normalize_knowledge_base_name


def build_vector_store(knowledge_base_name=None):
    normalized_name = normalize_knowledge_base_name(knowledge_base_name)
    knowledge_base_config = get_knowledge_base_config(normalized_name)
    vector_store = Chroma(
        collection_name=knowledge_base_config["collection_name"],
        embedding_function=DashScopeEmbeddings(model=config.embedding_model_name),
        persist_directory=knowledge_base_config["persist_directory"],
    )
    return normalized_name, knowledge_base_config, vector_store


class VectorStoreService(object):
    def __init__(self, knowledge_base_name=None):
        self.knowledge_base_name, self.knowledge_base_config, self.vector_store = build_vector_store(knowledge_base_name)

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": config.similarity_threshold})


if __name__ == "__main__":
    retriever = VectorStoreService().get_retriever()

    ret = retriever.invoke("早上好")
    print(ret)
