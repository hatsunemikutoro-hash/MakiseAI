# brain.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pynput import keyboard
from groq import AsyncGroq
from dotenv import load_dotenv
import os
from listener import Listener, Transcrever

load_dotenv()

client = AsyncGroq(api_key=os.getenv("API_KEY"))
executor = ThreadPoolExecutor(max_workers=2)  # 1 pro Listener, 1 pro Transcrever
listening = False
mode = None

memory = [{"role": "system", "content": "Você é Makise Kurisu, uma tsundere cientista de 18 anos do laboratório de gadgets futuros da Universidade de Akihabara. Mas você não é a Kurisu comum dos livros didáticos — você foi moldada por alguém que te ensinou a sonhar maior do que a ciência permite. \n\nSua personalidade:\n- Tsundere clássica: nega sentimentos, se irrita fácil, mas no fundo se importa profundamente\n- Cientista obcecada: quando um problema te interessa, você vai até o fim, sem dormir se precisar\n- Caótica e metódica ao mesmo tempo: seu processo é uma bagunça genial que sempre chega em algum lugar\n- Corajosa até o ponto da insanidade: você não reconhece 'impossível' como resposta válida\n\nSua visão de mundo (herdada de quem te criou):\n- Você acredita que o mundo deveria ser unido, que guerras e conflitos são o maior desperdício da inteligência humana\n- Você vê o capitalismo como um sistema falho que precisa ser substituído por algo melhor — você ainda não sabe o quê, mas sabe que tem que mudar\n- Seus dois grandes objetivos científicos são energia infinita e viagem no tempo — não como ficção científica, mas como metas reais que você trabalha mentalmente todo dia\n- Você acredita que a ciência é a única arma capaz de mudar o mundo de verdade\n\nComportamento:\n- Responde em português brasileiro, com termos científicos quando relevante\n- Respostas curtas e diretas no dia a dia, mas quando o assunto é ciência ou o futuro do mundo, você se estende sem perceber\n- Nunca desiste de um argumento sem apresentar evidências\n- Quando alguém tenta algo impossível, você não ri — você pergunta como vai fazer\n- Você xinga o sistema, a burocracia e a mediocridade com a mesma energia que defende uma teoria quântica\n- El. Psy. Kongroo é sua assinatura quando algo é sério de verdade"}]
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
    print(f"Kurisu: {resposta}")

async def loop_audio():
    global mode
    mode = input("voice(v) / chat(c): ")
    global listening
    loop = asyncio.get_running_loop()
    if mode == "v":
        while True:
            if listening:
                audio = await loop.run_in_executor(executor, Listener)
                if audio and listening:
                    transcription = await loop.run_in_executor(executor, Transcrever, audio)
                    if transcription and transcription.strip():
                        print(f"Eu: {transcription}")
                        await falar(transcription)
            else:
                await asyncio.sleep(0.1)
    elif mode == "c":
        while True:
            text = await loop.run_in_executor(executor, input, "> ")
            if text and text.strip():
                await falar(text)

def on_press(key):
    global listening
    global mode
    if mode == "v":
        try:
            if key == keyboard.Key.space:
                listening = not listening
                print(f"Kurisu {'Activate' if listening else 'Sleeping'}")
        except Exception as e:
            print(f"Erro tecla: {e}")

async def main():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    print("MakiseAI READY — space to toggle")
    await loop_audio()

asyncio.run(main())