from typing import List

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

class CodeRAG:
    def __init__(self) -> None:
        self.retriever = None

    def load(self) -> None:
        loader = GenericLoader.from_filesystem(
            '.',
            glob="**/*",
            suffixes=[".py"],
            parser=LanguageParser(language=Language.PYTHON),
        )

        documents = loader.load()

        python_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
        )

        texts = python_splitter.split_documents(documents)
        embeddings = Chroma.from_documents(texts, OpenAIEmbeddings(disallowed_special=()))
        self.retriever = embeddings.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 10},
        )

    def query(self, queries: List[str]) -> List[str]:
        documents = []

        for query in queries:
            documents.extend(self.retriever.invoke(query))

        return [str(document.metadata) + '\n' + document.page_content for document in documents]
