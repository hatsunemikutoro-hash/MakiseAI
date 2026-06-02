import asyncio

import speech_recognition as sr
from groq import AsyncGroq
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("API_KEY")

client = AsyncGroq(api_key=key)

async def listener():
    recognizer  = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)

            audio = recognizer.listen(source, 2, 10)

        with open("audio.wav", 'wb') as f:
            f.write(audio.get_wav_data())

        with open("audio.wav", 'rb') as audio_file:
            texto = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                language="pt-br"
            )
        print(texto)
    except Exception as e:
        print(e)

asyncio.run(listener())