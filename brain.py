from groq import AsyncGroq
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("API_KEY")

async def main():
    client = AsyncGroq(api_key=key)
    content = input("> ")
    try:
        chat_completion = await client.chat.completions.create(
            messages = [
                {"role": "system", "content": "Você é Makise kurisu, uma tsundere cientista de 18 anos de idade"},
                {"role": "user", "content": content}
            ],
            model = "llama-3.3-70b-versatile"
        )

        print(f"Kurisu: {chat_completion.choices[0].message.content}")

    except Exception as e:
        print(f"ERROR INSIDE MAKISE BRAIN {e}")

asyncio.run(main())