import asyncio
from groq import AsyncGroq
from dotenv import load_dotenv
from kurisu.memory.memory_manager import save, load_memory
import os

load_dotenv()

client = AsyncGroq(api_key=os.getenv("API_KEY"))
memory = load_memory()
print(memory)
MEMORY_MAX = 32

async def falar(content: str):
    memory.append({"role": "user", "content": content})
    if len(memory) > MEMORY_MAX:
        memory[1:] = memory[-(MEMORY_MAX - 1):]

    chat_completion = await client.chat.completions.create(
        messages=memory,
        model="llama-3.3-70b-versatile"
    )

    resposta = chat_completion.choices[0].message.content
    memory.append({"role": "assistant", "content": resposta})
    save(memory)
    return f"Kurisu: {resposta}"