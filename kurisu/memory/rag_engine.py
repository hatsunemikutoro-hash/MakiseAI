import asyncio
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="S:/Vscode/MakiseAI/kurisu/memory/amadeus_cortex", embedding_function=embeddings)


async def consultar_data(pergunta):
    resultados = await asyncio.to_thread(
        vector_db.similarity_search_with_score,
        pergunta,
        k=3
    )

    if not resultados:
        return "Nenhum dado encontrado."

    doc, score = resultados[0]

    print(f"DEBUG: Pergunta: '{pergunta}' | Melhor Score: {score}")

    if score < 1.0:
        return doc.page_content
    else:
        return f"Não encontrei nada com relevância suficiente (Score: {score})"


def salvar_no_cerebro(texto):
    db = Chroma(persist_directory="S:/Vscode/MakiseAI/kurisu/memory/amadeus_cortex",
                embedding_function=embeddings)

    db.add_texts([texto])
    print(">>> Kurisu: Informação inserida no banco vetorial.")
