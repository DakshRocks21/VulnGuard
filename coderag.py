from typing import List

from langchain_chroma import Chroma
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser

class CodeRAG:
    def __init__(self) -> None:
        self.retriever = None
        self._load()

    def _load(self) -> None:
        loader = GenericLoader.from_filesystem(
            '.',
            glob="*.py",  # TODO: Change this to **/*.py
            suffixes=[".py"],
            parser=LanguageParser(language=Language.PYTHON),
        )

        documents = loader.load()

        python_splitter = RecursiveCharacterTextSplitter(
            chunk_size=50,
            chunk_overlap=5,
        )

        texts = python_splitter.split_documents(documents)
        embeddings = Chroma.from_documents(texts, OpenAIEmbeddings(disallowed_special=()))
        self.retriever = embeddings.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 8},
        )

    def query(self, queries: List[str]) -> str:
        documents = []

        for query in queries:
            documents.extend(self.retriever.invoke(query))

        return '\n'.join([str(document.metadata) + '\n' + document.page_content for document in documents])
