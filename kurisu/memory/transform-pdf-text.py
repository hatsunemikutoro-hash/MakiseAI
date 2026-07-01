from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def processar_pdf(caminho_pdf):
    # 1. Carrega o PDF
    loader = PyPDFLoader(caminho_pdf)
    documentos = loader.load()

    # 2. Fragmenta com precisão (o 'overlap' garante que não se perca contexto na quebra)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documentos)

    # 3. Embedding (transforma texto em vetores numéricos)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Salva no banco (o cérebro)
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./amadeus_cortex"
    )
    print(f"Dados do {caminho_pdf} assimilados com sucesso.")

processar_pdf("S:\\Vscode\\MakiseAI\\kurisu\\memory\\books\\ManifestoComunista.pdf")