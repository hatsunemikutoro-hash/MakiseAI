from pynput import keyboard
from kurisu.brain_func.state import state
import re
from duckduckgo_search import DDGS

ferramentas = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Busca informações em tempo real na internet. Use sempre que o usuário perguntar sobre eventos atuais, notícias ou fatos que você não sabe.",
            "parameters": {
                "type": "object",
                "properties": {
                    "termo": {
                        "type": "string",
                        "description": "O termo ou frase curta para pesquisar no buscador.",
                    }
                },
                "required": ["termo"],
            },
        },
    }
]

def search(termo: str) -> str:
    try:
        with DDGS as ddgs:
            resultados = [r for r in ddgs.text(termo, max_results=3)]

            contexto = ""
            for i, r in enumerate(resultados, 1):
                contexto += f"Resultado {i}: {r['title']}\nResumo: {r['body']}\n\n"
                return contexto
    except Exception as e:
        return "erro ao acessar o steins gate."

def on_press(key):
    if state.mode == "v":
        try:
            if key == keyboard.Key.space:
                listening = not state.listening
                print(f"Kurisu {'Activate' if listening else 'Sleeping'}")
        except Exception as e:
            print(f"Erro tecla: {e}")


def filtrar_resposta_kurisu(texto_da_ia):
    texto_limpo = re.sub(r'<think>.*?</think>', '', texto_da_ia, flags=re.DOTALL)
    texto_limpo = re.sub(r'<thought>.*?</thought>', '', texto_limpo, flags=re.DOTALL)

    texto_limpo = texto_limpo.replace('[Kurisu]:', '')
    texto_limpo = texto_limpo.replace('*Kurisu*:', '')
    texto_limpo = texto_limpo.replace('Kurisu:', '')

    return texto_limpo.strip()
