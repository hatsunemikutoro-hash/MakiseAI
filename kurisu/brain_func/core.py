import asyncio
from ollama import AsyncClient
from groq import AsyncGroq
from dotenv import load_dotenv
from datetime import datetime
from kurisu.memory.memory_manager import save, load_memory, prompt_initial, save_facts, load_facts, \
    buscar_fatos_relevantes
import os
import json

from kurisu.utils import ferramentas, search

load_dotenv()

memory = load_memory()
model = "qwen2.5:7b"
MEMORY_MAX = 8

async def extract_fact(content):
    prompt = """Analise essa conversa e extraia fatos importantes e permanentes SOMENTE do usuario, e force a terceira pessoa (O usuario gosta, etc), ignore a assistente.
    Retorne APENAS um JSON assim, sem mais nada:
    {"fatos": ["fato 1", "fato 2"]}
    
    Responda APENAS com um objeto JSON válido. Não adicione comentários, não adicione explicações. Se a estrutura não fechar com uma chave '}', o sistema falha. Seja preciso
    Foque em: preferências, sentimentos recorrentes, eventos importantes, informações pessoais."""

    response = await AsyncClient().chat(
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": str(content)}
        ],
        model=model
    )

    text = response['message']['content']

    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        new_facts = json.loads(text)["fatos"]
        save_facts(new_facts)
    except json.JSONDecodeError:
        print(">>> erro no json, llm retornou:", text)


async def falar(content: str):
    agora_hora = datetime.now().strftime("%H:%M")
    agora_completo = datetime.now().strftime("%d/%m/%Y %H:%M")

    memory.append({"role": "user", "content": f"[{agora_hora}] {content}"})

    if len(memory) > MEMORY_MAX:
        memory[:] = memory[-MEMORY_MAX:]

    facts = await buscar_fatos_relevantes(content)

    system_content = (
        f"{prompt_initial}\n\n"
        f"Pesquisa sobre o usuario (conversas anteriores):\n{facts}\n\n"
        f"Linha do tempo atual de referência: {agora_completo} (Não cite isso do nada)."
    )

    chat_completion = await AsyncClient().chat(
        messages=[
            {"role": "system", "content": system_content},
            *memory
        ],
        model=model,
        options={
            "temperature": 0.4,
            "top_p": 0.9,
            "repeat_penalty": 1.15
        },
        tools=ferramentas
    )

    mensagem_ia = chat_completion['message']

    if hasattr(mensagem_ia, 'tool_calls') and mensagem_ia.tool_calls:
        print("\n[ALERT] A assistente Kurisu acionou o Tool Calling!")

        # Convertendo o objeto Message em um dict puro do Python para não quebrar o save(memory)
        if hasattr(mensagem_ia, 'model_dump'):
            memory.append(mensagem_ia.model_dump())
        else:
            memory.append(dict(mensagem_ia))

        for call in mensagem_ia.tool_calls:
            nome_funcao = call['function']['name']
            argumentos = call['function']['arguments']

            print(f"-> Executando gadget: {nome_funcao}")
            print(f"-> Parâmetros decodificados: {argumentos}")

            if nome_funcao == "search":
                resultado_busca = search(argumentos['termo'])

                memory.append({
                    "role": "tool",
                    "name": nome_funcao,
                    "content": resultado_busca
                })

        segunda_completion = await AsyncClient().chat(
            messages=[{"role": "system", "content": system_content}, *memory],
            model=model,
            options={"temperature": 0.4, "top_p": 0.9, "repeat_penalty": 1.15}
        )

        raw_resposta = segunda_completion['message']['content']

    else:
        raw_resposta = mensagem_ia['content'] if 'content' in mensagem_ia else mensagem_ia.content
    # =========================================================================

    if "</think>" in raw_resposta:
        resposta_limpa = raw_resposta.split("</think>")[-1].strip()
    else:
        resposta_limpa = raw_resposta.strip()

    memory.append({"role": "assistant", "content": resposta_limpa})
    save(memory)

    if "!save_mem" in content.strip().lower():
        await extract_fact(memory)

    return f"{resposta_limpa}"