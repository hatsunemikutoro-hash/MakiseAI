from concurrent.futures import ThreadPoolExecutor
from listener import Listener, Transcrever
from kurisu.brain_func.core import *
from utils import *
from kurisu.brain_func.state import state

executor = ThreadPoolExecutor(max_workers=2)  # 1 pro Listener, 1 pro Transcrever

async def loop_audio():
    state.mode = input("voice(v) / chat(c): ")
    loop = asyncio.get_running_loop()
    if state.mode == "v":
        while True:
            if state.listening:
                audio = await loop.run_in_executor(executor, Listener)
                if audio and state.listening:
                    transcription = await loop.run_in_executor(executor, Transcrever, audio)
                    if transcription and transcription.strip():
                        print(f"Eu: {transcription}")
                        print(await falar(transcription))
            else:
                await asyncio.sleep(0.1)
    elif state.mode == "c":
        while True:
            text = await loop.run_in_executor(executor, input, "> ")
            if text and text.strip():
                response = await falar(text)
                print(response)

async def main():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    print("Amadeus kurisu READY — space to toggle")
    await loop_audio()

asyncio.run(main())