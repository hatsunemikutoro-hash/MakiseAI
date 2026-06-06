import json
import os

caminho_memories = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(caminho_memories, "prompt_initial"), 'r', encoding='utf-8') as file:
    prompt_initial = file.read()

vies = [{"role": "system", "content": prompt_initial}]
print(caminho_memories)

def load_memory():
    if os.path.exists(os.path.join(caminho_memories, "memories.json")):
        with open(os.path.join(caminho_memories, "memories.json"), 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    else:
        with open(os.path.join(caminho_memories, "memories.json"), 'w', encoding='utf-8') as f:
            json.dump(vies, f, ensure_ascii=False)
            return vies

def save(data):
    with open(os.path.join(caminho_memories, "memories.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

