import asyncio
from ollama import AsyncClient
from groq import AsyncGroq
from dotenv import load_dotenv
from datetime import datetime
import os
import json

from kurisu.memory import memory_manager
from kurisu.memory import rag_engine
from kurisu.utils import ferramentas, search, think

load_dotenv()

memory = memory_manager.load_memory()
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
        memory_manager.save_facts(new_facts)
    except json.JSONDecodeError:
        print(">>> erro no json, llm retornou:", text)

async def stream_response(messages):
    stream = await AsyncClient().chat(
        model=model,
        messages=messages,
        stream=True,
        tools=ferramentas,
        options={"temperature": 0.4},
    )

    texto = ""
    tool_calls = []

    async for chunk in stream:
        msg = chunk.message

        if msg.tool_calls:
            tool_calls.extend(msg.tool_calls)

        if msg.content:
            texto += msg.content
            yield ("text", msg.content)

    yield ("done", {
        "content": texto,
        "tool_calls": tool_calls
    })

async def falar(content: str):
    agora_hora = datetime.now().strftime("%H:%M")
    agora_completo = datetime.now().strftime("%d/%m/%Y %H:%M")

    memory.append({
        "role": "user",
        "content": f"[{agora_hora}] {content}"
    })

    if len(memory) > MEMORY_MAX:
        memory[:] = memory[-MEMORY_MAX:]

    persona_ativa = memory_manager.current_persona.replace("amadeus_", "")

    facts, rag_data = await asyncio.gather(
        memory_manager.buscar_fatos_relevantes(content),
        rag_engine.consultar_data(content, persona=persona_ativa)
    )

    prompt_atual = memory_manager.vies[0]["content"]

    system_content = (
        f"{prompt_atual}\n\n"
        f"Pesquisa sobre o usuario:\n{facts}\n\n"
        f"Pesquisa no banco de dados (RAG):\n{rag_data}\n\n"
        f"Linha do tempo atual: {agora_completo} (Não cite isso do nada)."
    )

    messages = [
        {"role": "system", "content": system_content},
        *memory
    ]

    full_response = ""
    tool_calls = []

    # ================= PRIMEIRA GERAÇÃO =================

    async for tipo, data in stream_response(messages):

        if tipo == "text":
            full_response += data
            yield data

        else:
            tool_calls = data["tool_calls"]

    # Se não chamou nenhuma tool acabou.
    if not tool_calls:
        memory.append({
            "role": "assistant",
            "content": full_response
        })
        memory_manager.save(memory)
        return

    # Salva a resposta parcial + tool calls
    memory.append({
        "role": "assistant",
        "content": full_response,
        "tool_calls": [
            {
                "type": "function",
                "function": {
                    "name": t.function.name,
                    "arguments": t.function.arguments
                }
            }
            for t in tool_calls
        ]
    })

    # ================= EXECUTA TOOLS =================

    for tool in tool_calls:

        nome = tool.function.name
        args = tool.function.arguments

        if isinstance(args, str):
            args = json.loads(args)

        if nome == "search":

            termo = args["termo"]

            yield (
                f"\n[dim #00ffff]"
                f"* Pesquisando '{termo}'... *"
                f"[/dim #00ffff]\n"
            )

            resultado = search(termo)

        elif nome == "think":

            yield (
                "\n[dim #ffaa00]"
                "* Analisando profundamente o problema... *"
                "[/dim #ffaa00]\n"
            )

            resultado = await think(args["prompt"])

        else:
            continue

        memory.append({
            "role": "tool",
            "name": nome,
            "content": resultado
        })

    # ================= SEGUNDA GERAÇÃO =================

    full_response = ""

    messages = [
        {"role": "system", "content": system_content},
        *memory
    ]

    async for tipo, data in stream_response(messages):

        if tipo == "text":
            full_response += data
            yield data

    memory.append({
        "role": "assistant",
        "content": full_response
    })

    memory_manager.save(memory)