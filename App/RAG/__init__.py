import os
os.environ["OPENAI_API_KEY"] = ""

import re

import logging
from langchain_openai import OpenAI
from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores.chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.storage import InMemoryStore
# from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.vectorstores.faiss import FAISS
from langchain.docstore.document import Document
# from langchain.chains import RetrievalQA
from langchain_core.embeddings import Embeddings

from App.RAG.scraper import Roupa

import logging

logger = logging.getLogger("main")

# def pretty_print_docs(docs):
#     print(f"\n{'-' * 100}\n".join([f"Document {i+1}:\n" + d.page_content for i, d in enumerate(docs)]))

from typing import List

faiss_path = './App/RAG/Faiss'

def update_vector_db(docs: List[Document], embeddings: Embeddings):
    vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)
    vectorstore.save_local(faiss_path)
    return vectorstore

def extract_roupa_values(text):
  """Extracts ROUPA values from the given text, handling both single-item and comma-separated formats.

  Args:
      text: The text to extract ROUPA values from.

  Returns:
      A list of extracted ROUPA values.
  """
  # Extract ROUPA values using regular expressions
  roupa_values = re.findall(r"ROUPA:(.*)", text, re.DOTALL)
  
  # Split comma-separated values
  for i in range(len(roupa_values)):
    roupa_values[i] = roupa_values[i].strip().split(", ")
  
  # Flatten the list
  roupa_values = [item for sublist in roupa_values for item in sublist]
  return roupa_values

def do_search(situacao: str) -> List[Roupa]:
    """Que roupas combinam com a situação :situacao:?
    
    Args: 
        situacao: Situação a ser analizada
    
    Retorna lista de roupas da La Moda adequadas"""

    logger.warning(f"Pesquisa de situação >> {situacao}")
    
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""Você é uma consultora de moda. Seu trabalho é retornar quais vestimentas são adequadas para uma situação. Dê respostas breves. Não retorne acessórios. Retorne as roupas no formato ROUPA: roupa.
Situação: {question}"""
    )

    qa = LLMChain(
        llm=OpenAI(model_name="gpt-3.5-turbo-instruct", temperature=0),
        prompt=QUERY_PROMPT
    )

    a = qa.invoke(situacao)
    # print(a)
    ans = a['text']
    logger.warning(f"Resposta da IA >> {a}")
    logger.warning(f"Resposta da IA >> {ans}")
    # print(ans)

    logger.info("Carregando docs")
    loader = DirectoryLoader('./App/RAG/docs', glob="**/*.txt", loader_cls=TextLoader, show_progress=True)

    docs = loader.load()

    embeddings = OpenAIEmbeddings(chunk_size=600)
    # vectorstore = Chroma(collection_name="full_documents", embedding_function=embeddings)
    # vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)
    vectorstore = FAISS.load_local(faiss_path, embeddings)
    store = InMemoryStore()
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=0)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=40)
    global retriever # :X
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )

    retriever.add_documents(docs)

    # memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer')

    # links = []
    roupas_ia = extract_roupa_values(ans)
    
    logger.warning(roupas_ia)

    roupas: List[Roupa] = []
    for roupa_ia in roupas_ia:
        docs = retriever.get_relevant_documents(roupa_ia)
        logger.info(f"Encontrados: {len(docs)} documentos")

        for doc in docs:
            print(doc)
            roupa = Roupa.from_dict(Roupa.from_doc(doc.page_content))

        roupas.append(roupa)
    return roupas
