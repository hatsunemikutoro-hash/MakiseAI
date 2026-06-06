from pynput import keyboard
from kurisu.brain_func.state import state

def on_press(key):
    if state.mode == "v":
        try:
            if key == keyboard.Key.space:
                listening = not state.listening
                print(f"Kurisu {'Activate' if listening else 'Sleeping'}")
        except Exception as e:
            print(f"Erro tecla: {e}")