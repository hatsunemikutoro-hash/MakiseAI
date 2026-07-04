from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DB_DIR = "S:/Vscode/MakiseAI/kurisu/memory/amadeus_cortex"

def aprender_livro(caminho_pdf, persona="kurisu"):
    """
    Carrega um PDF e o assimila na coleção correta da Amadeus.
    Se as pastas ou coleções não existirem, o Chroma as criará automaticamente
    """
    nome_da_colecao = f"amadeus_{persona}"
    
    print(f"[{persona.upper()}] Iniciando leitura do arquivo de dados: {caminho_pdf}...")

    loader = PyPDFLoader(caminho_pdf)
    documentos = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documentos)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR,
        collection_name=nome_da_colecao
    )
    
    print(f"Sucess [{persona.upper()}].")


aprender_livro(
    caminho_pdf="S:\\Vscode\\MakiseAI\\kurisu\\memory\\books\\Skuld\\manualdeprimeirossocorros.pdf",
    persona="skuld"
)