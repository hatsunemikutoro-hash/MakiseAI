import json
import os
import aiofiles

caminho_memories = os.path.dirname(os.path.abspath(__file__))

character_prompt = "prompt_initial_chaos"

with open(os.path.join(caminho_memories, character_prompt), 'r', encoding='utf-8') as file:
    prompt_initial = file.read()

vies = [{"role": "system", "content": prompt_initial}]

def save_facts(new_facts):
    caminho = os.path.join(caminho_memories, "facts.json")

    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            existing_facts = json.load(f)
    else:
        existing_facts = []

    allFacts = list(set(existing_facts + new_facts))

    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(allFacts, f, ensure_ascii=False, indent=2)

def load_facts():
    caminho = os.path.join(caminho_memories, "facts.json")

    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


async def buscar_fatos_relevantes(pergunta):
    caminho = os.path.join(caminho_memories, "facts.json")
    async with aiofiles.open(caminho, mode='r', encoding='utf-8') as f:
        conteudo = await f.read()
        fatos = json.loads(conteudo)

    palavras_pergunta = pergunta.lower().split()
    relevantes = [
        f for f in fatos
        if any(palavra in f.lower() for palavra in palavras_pergunta)
    ]

    return relevantes

def load_memory():
    if os.path.exists(os.path.join(caminho_memories, "memories.json")):
        with open(os.path.join(caminho_memories, "memories.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [m for m in data if m["role"] != "system"]
    else:
        with open(os.path.join(caminho_memories, "memories.json"), 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)
            return []

def save(data):
    with open(os.path.join(caminho_memories, "memories.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def wipe():
    with open(os.path.join(caminho_memories, "memories.json"), 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False)

