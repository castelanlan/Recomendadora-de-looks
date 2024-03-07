<<<<<<< HEAD
import os
os.environ["OPENAI_API_KEY"] = ""

=======
>>>>>>> 76b895a (re organizando algumas coisas)
import re
import time
import logging
from typing import List, Tuple

from App import Roupa, CustomFormatter

rag_logger = logging.Logger("RAG")
rag_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
rag_logger.addHandler(ch)

faiss_path = './App/RAG/Faiss'

from openai import OpenAI as OpenAIClient
from langchain_openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.storage import InMemoryStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.vectorstores.faiss import FAISS
from langchain.docstore.document import Document
from langchain_core.embeddings import Embeddings

def update_vector_db(docs: List[Document], embeddings: Embeddings):
    vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)
    vectorstore.save_local(faiss_path)
    return vectorstore

def extract_roupa_values(text: str):
    """Extracts ROUPA values from the given text, handling both single-item and comma-separated formats.

    Args:
        text: The text to extract ROUPA values from.

    Returns:
        A list of extracted ROUPA values.
"""
    # Extract ROUPA values using regular expressions
    # roupa_values = re.findall(r"ROUPA:(.*)", text, re.DOTALL)
    roupa_values = text.strip().split("\n")

    # Split comma-separated values
    for i in range(len(roupa_values)):
        roupa_values[i] = roupa_values[i].split(", ")

    # Flatten the list
    roupa_values = [item for sublist in roupa_values for item in sublist]
    return roupa_values

def pre_selecao(situacao: str) -> List[Roupa]:
    """Que roupas combinam com a situação :situacao:?
    
    Args: 
        situacao: Situação a ser analizada
    
    Retorna lista de roupas da La Moda adequadas"""

    rag_logger.warning(f"Pesquisa de situação >> {situacao}")
    
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""Você é uma inteligência que gera palavras para serem procuradas num banco de dados. Seu trabalho é retornar quais roupas seriam adequadas para uma situação.
        Dê respostas SIMPLES de no máximo 2 palavras. Além de vestimentas, você pode retornar adjetivos em geral, por exemplo "casual", "colorido", "elegante".
        Não retorne acessórios, retorne as palavras no formato 'Vestido longo, colorido, terno preto, salto, etc...'. Seja criativo, procure dar entre 5 a 10 respostas. Não numere as respostas.
Situação: {question}"""
    )

    qa = LLMChain(
        llm=OpenAI(model_name="gpt-3.5-turbo-instruct", temperature=0),
        prompt=QUERY_PROMPT
    )

    a = qa.invoke(situacao)
    ans: str = a['text']
    rag_logger.info(f"Resposta da IA >> {ans.strip()}")

    rag_logger.info("Carregando retriever")
    inicial = time.perf_counter()
    loader = DirectoryLoader('./App/RAG/docs', glob="**/*.txt", loader_cls=TextLoader)

    rag_logger.info("Retriever > Carregar docs")
    docs = loader.load()
    # docs_file = loader.load()
    # docs_splitter = CharacterTextSplitter("\n")
    # docs = docs_splitter.split_documents(docs_file)

    rag_logger.info("Retriever > Init retriever")
    embeddings = OpenAIEmbeddings(chunk_size=600)
    # vectorstore = Chroma(collection_name="full_documents", embedding_function=embeddings)
    # vectorstore = FAISS.from_documents(documents=docs, embedding=embeddings)
    vectorstore = update_vector_db(docs, embeddings)
    # vectorstore = FAISS.load_local(faiss_path, embeddings)
    store = InMemoryStore()
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=640, chunk_overlap=0)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=40)
    global retriever # :X
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )

    rag_logger.info("Retriever > Carregar docs no retriever")
    retriever.add_documents(docs)
    final = time.perf_counter()
    delta = final - inicial
    rag_logger.info(f"Retriever carregado em {final}s")
    

    # memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer')

    # links = []
    roupas_ia = extract_roupa_values(ans)
    
    rag_logger.warning(roupas_ia)

    roupas: List[Roupa] = []
    for roupa_ia in roupas_ia:
        docs = retriever.get_relevant_documents(roupa_ia)
        rag_logger.info(f"Encontrados: {len(docs)} documentos para \"{roupa_ia}\"")

        for doc in docs:
            try:
                roupa = Roupa.from_dict(Roupa.from_doc(doc.page_content))
                roupas.append(roupa)
            except KeyError as e:
                rag_logger.error(f"Erro neste item {doc.page_content} > {e}")

    return roupas

class RoupaAvaliada(Roupa):
    def __init__(self, href: str, titulo: str, valor: str, desc: str, parcela: str, imgs: List[str], colecao: str = None,
                nota: int=None, justificativa: str=None) -> None:
        self.nota: int = nota
        self.justificativa: str = justificativa
        super().__init__(href, titulo, valor, desc, parcela, imgs, colecao)

    def chat_avalia(self, situ):
        nota, justificativa = self.vision(self.imgs[0], situ, self.titulo)
        self.nota = nota
        self.justificativa = justificativa

    @staticmethod
    def vision(img_link: str, situacao: str, roupa: str) -> Tuple[str, str]:
        rag_logger.info(f"Chamada para Vision | {img_link}")
        client = OpenAIClient()
        response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
            "role": "user",
            "content": [
                {"type": "text", "text": f"""Você é uma ferramenta para classificar roupas. De um valor de 0 a 10 para esta roupa baseado na situação e uma justificativa. Se a roupa é perfeita para a situação, recebe nota 10, se a roupa não se adequa para a situação, é nota 0. De o valor no formato x/10, por exemplo: "NOTA: 9/10"
                 A justificativa deve ser num tom amigável, evite falar diretamente da nota na justificativa.  

Roupa: {roupa}
Situação: {situacao}"""},
                # {"type": "text", "text": f"""Give a 0-10 value for these clothes based on a situation, if it's perfect for the situation, it's a 10, if it doesn't fit the situation at all, it's a 0.
# 
# Situation: {situacao}"""},
                {
                "type": "image_url",
                "image_url": {
                    "url": img_link,
                },
                },
            ],
            }
        ],
        max_tokens=300,
        )
        try:
            nota = re.findall("NOTA: (\d+\/\d+)", response.choices[0].message.content)[0]
            nota = int(nota.strip("NOTA: ").split("/")[0])
        except IndexError:
            nota = 5
        just = response.choices[0].message.content
        return nota, just
        # return 10, "Bela roupa"

def avaliar(roupas: List[Roupa], situacao) -> List[Roupa]:
    rag_logger.info(f"Avaliando {len(roupas)} roupas...")
    roupas_avaliadas = []

    for roupa in roupas:
        roupa = RoupaAvaliada(roupa.href, roupa.titulo, roupa.valor, roupa.desc, roupa.parcela, roupa.imgs, colecao=None, nota=0, justificativa="")
        rag_logger.info(f"Avaliando {roupa.titulo}")
        roupa.chat_avalia(situacao)
        roupas_avaliadas.append(roupa)

        if len(roupas_avaliadas) > 6:
            break
    
    roupas_ordenadas = sorted(roupas_avaliadas, key=lambda roupa: roupa.nota, reverse=True)

    return roupas_ordenadas