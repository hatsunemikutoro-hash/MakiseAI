# listener.py
import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

client = Groq(api_key=os.getenv("API_KEY"))  # env já carregado pelo brain

_recognizer = sr.Recognizer()
_recognizer.energy_threshold = 1000
_recognizer.dynamic_energy_threshold = False
_mic = sr.Microphone()

with _mic as source:
    _recognizer.adjust_for_ambient_noise(source, duration=0.5)

def Transcrever(audio: sr.AudioData) -> str:
    return client.audio.transcriptions.create(
        model="whisper-large-v3-turbo",  # 4x mais rápido
        file=("audio.wav", audio.get_wav_data()),
        language="pt"
    ).text

def Listener() -> sr.AudioData | None:
    try:
        with _mic as source:
            print("Pode falar...")
            audio = _recognizer.listen(source, timeout=5, phrase_time_limit=10)
        return audio
    except sr.WaitTimeoutError:
        print("Não ouvi nada.")
        return None
    except Exception as e:
        print(f"Erro no Listener: {e}")
        return None