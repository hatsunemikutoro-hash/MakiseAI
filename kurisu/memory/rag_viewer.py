import chromadb

PERSIST_DIR = "amadeus_cortex"

try:
    client = chromadb.PersistentClient(path=PERSIST_DIR)

    colecoes = client.list_collections()
    print("=== COLEÇÕES ENCONTRADAS ===")
    for col in colecoes:
        print(f"- {col.name}")
    print("============================\n")

    NOME_COLECAO = colecoes[0].name if colecoes else "sua_colecao"
    collection = client.get_collection(name=NOME_COLECAO)

    dados = collection.get()

    print(f"=== DADOS DA COLECÃO '{NOME_COLECAO}' ===")
    print(f"Total de registros: {len(dados['ids'])}\n")

    for i in range(len(dados['ids'])):
        print(f"[{i + 1}] ID: {dados['ids'][i]}")
        print(f"    Conteúdo: {dados['documents'][i]}")
        if dados['metadatas'] and dados['metadatas'][i]:
            print(f"    Metadata: {dados['metadatas'][i]}")
        print("-" * 40)

except Exception as e:
    print(f"Erro ao ler o banco de dados: {e}")