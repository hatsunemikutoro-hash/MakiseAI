import asyncio
from ollama import AsyncClient
from groq import AsyncGroq
from dotenv import load_dotenv
from datetime import datetime
from kurisu.memory.memory_manager import save, load_memory, prompt_initial, save_facts, load_facts, \
    buscar_fatos_relevantes
import os
import json

from kurisu.memory.rag_engine import consultar_data
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


#  esse falar ja foi um dia um codigo de 5 linhas

async def falar(content: str):
    agora_hora = datetime.now().strftime("%H:%M")
    agora_completo = datetime.now().strftime("%d/%m/%Y %H:%M")

    memory.append({"role": "user", "content": f"[{agora_hora}] {content}"})

    if len(memory) > MEMORY_MAX:
        memory[:] = memory[-MEMORY_MAX:]

    facts, rag_data = await asyncio.gather(
        buscar_fatos_relevantes(content),
        consultar_data(content)
    )

    system_content = (
        f"{prompt_initial}\n\n"
        f"Pesquisa sobre o usuario (conversas anteriores):\n{facts}\n\n"
        f"Pesquisa no banco de dados (RAG): \n{rag_data}\n\n"
        f"Linha do tempo atual de referência: {agora_completo} (Não cite isso do nada)."
    )

    stream = await AsyncClient().chat(
        messages=[{"role": "system", "content": system_content}, *memory],
        model=model,
        stream=True,
        tools=ferramentas,
        options={"temperature": 0.4}
    )

    full_response = ""
    tool_calls_buffer = []

    async for chunk in stream:
        msg = chunk.get('message', {})

        if 'tool_calls' in msg and msg['tool_calls']:
            tool_calls_buffer.extend(msg['tool_calls'])

        parte = msg.get('content', '')
        if parte:
            full_response += parte
            yield parte

    if tool_calls_buffer:
        safe_tools = []
        for t in tool_calls_buffer:
            f_name = t.function.name if hasattr(t, 'function') else t['function']['name']
            f_args = t.function.arguments if hasattr(t, 'function') else t['function']['arguments']


            if isinstance(f_args, str):
                try:
                    f_args = json.loads(f_args)
                except:
                    pass  # Se falhar, mantém como string e torce pro melhor

            safe_tools.append({
                "type": "function",
                "function": {
                    "name": f_name,
                    "arguments": f_args
                }
            })

        memory.append({
            "role": "assistant",
            "content": full_response,
            "tool_calls": safe_tools
        })

        for tool in safe_tools:
            nome_func = tool['function']['name']
            if nome_func == 'search':
                args = tool['function']['arguments']
                termo = args.get('termo', '')

                yield f"\n[dim #00ffff]* Acessando a rede para buscar: '{termo}'... *[/dim #00ffff]\n"

                # Executa a pesquisa
                resultado = search(termo)

                memory.append({
                    "role": "tool",
                    "content": resultado,
                    "name": nome_func
                })

        stream_final = await AsyncClient().chat(
            messages=[{"role": "system", "content": system_content}, *memory],
            model=model,
            stream=True,
            options={"temperature": 0.4}
        )

        final_text = ""
        async for chunk in stream_final:
            parte = chunk['message'].get('content', '')
            if parte:
                final_text += parte
                yield parte

        full_response = final_text

    memory.append({"role": "assistant", "content": full_response})
    save(memory)