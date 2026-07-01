import time
import asyncio
from textual.app import App
from textual.widgets import Header, Footer, Static, Input
from textual.containers import VerticalScroll

# Importando a função geradora
from kurisu.brain_func.core import falar, memory
from kurisu.memory.memory_manager import wipe


class AmadeusKurisu(App):
    CSS = """
    Screen { background: #0a0a1a; }

    #chat_container {
        height: 1fr;
        border: ascii #FF003C;
        background: #0D0D0D;
        padding: 1;
    }

    /* Estilos opcionais para separar as mensagens visualmente */
    .msg_user { margin-top: 1; }
    .msg_amadeus { }
    .msg_info { margin-bottom: 1; }

    #status_bar {
        height: 1;
        background: #1a0a1a;
        color: #ff00ff;
        padding-left: 1;
        text-style: italic;
    }

    Input { 
        border: round #FF003C;
        background: #0D0D0D; 
        color: #ffa400;
    }
    """

    def compose(self):
        yield Header()
        # Usamos o VerticalScroll como um "container vazio" que vai receber as mensagens
        with VerticalScroll(id="chat_container"):
            pass
        yield Static(id="status_bar")
        yield Input(placeholder="user@makise-lab:~$", id="terminal_input")
        yield Footer()

    async def on_mount(self):
        container = self.query_one("#chat_container", VerticalScroll)
        GOLD = "#FFD700"

        banner_text = rf"""[bold {GOLD}]
                                                         :
                                                       :::
                          -:::----::::               :-*%-
                     -:-+*%%%@%%%@@%*%#+:::        --*@@#-
                  :-=*@@##@@%@%%#@%*+@@%+%#--:   --+@@@@*-
                :-*%*#*%@*+++++++++++#%#@@###*-:=*@@@@@@+:
               -*@*@@%*=*#+=--+@@@@#-+#==*%@@@@*+@@@@@@%- 
             :=*%@@%+*@@+::::::---=-::::+*=#@@@=%@@@@@@+: 
            -=@@@#=+@@@%+:::::::::::::::-#@%=++@@@@@@@#:  
           :=%#*%=%--*-::::::::::::::::::+@@=#@@@@@=#%:   
          :-%@@@+#-::::::::=*%@@@@%*=:::::-+@@@@@*+@+-:   
          :%#%#+*=:::::::=@@@@@@@@@@@%=::=%@@@@#+%@@#-    
         :=@@@%-@#=:::::+@@@@@@@@@@@@@#=%@@@@#-#+@@@%=    
         :*@@@**@@#::::=%@@@@@@@@@@@%+#@@@@#=-=#+%@@@=    
         :*@@@+#@@*::::=@@@@@@@@@@#=%@@@@#-:-#@@+*##%+:   
         :*@@@**+::::::-%@@@@@@@*=%@@@@*::::-%@@=#%%#=    
         :=@@@%-#-::::::=@@@@%+*@@@@%++-:::::=*#+@@@%=    
          :#@@@**+:::::::-#*=@@@@@*=%#-:::::::#-#+%**-    
          :-@@@@+*+*#-:::=*@@@@#==*=::::::::-*=#%@@@=:    
           :=@@@@+#@@*-*@@@@#=-:::::::::-##+++*##%@=:     
           :=+@@***-+@@@@#-:::::::::::-%@@@#=#@@@@-:      
         :-#++=*%%@@++++=:::=*++=::::::*@*+##*#*%=:       
        -=%#-*%*+@%#@@#==*%#@@@@@=-+%#+=*%%@@*%=-         
        -#@%#+-:::+@@#@#@%*+=-=====+#*#@@%##%+-           
        ::-:       :=+#@@#%@@+#%@%#%@#@#@%+-:             
                      :--+#@@@#@@%*@@#=--:                
                           ::::::::::                     [/]"""

        # Injetamos o banner e a mensagem inicial de forma independente
        await container.mount(Static(banner_text, markup=True))
        await container.mount(
            Static("[bold #ff7700]>>> Sistema Amadeus online...[/bold #ff7700]", markup=True, classes="msg_info"))

    async def run_spinner(self, status_widget):
        spinner = ["|", "/", "-", "\\"]
        i = 0
        while True:
            status_widget.update(f"[bold #ff7700]{spinner[i % 4]} Kurisu is Thinking...")
            i += 1
            await asyncio.sleep(0.1)

    async def processar_comando(self, comando: str):
        partes = comando.split()
        cmd = partes[0].lower()

        if cmd == "/wipe":
            wipe()
            memory.clear()
            container = self.query_one("#chat_container", VerticalScroll)
            await container.mount(Static("[dim]Memória do sistema purgada.[/dim]", classes="msg_info"))
            container.scroll_end()


    async def on_input_submitted(self, event: Input.Submitted):
        user_text = event.value
        if not user_text: return

        container = self.query_one("#chat_container", VerticalScroll)
        status = self.query_one("#status_bar", Static)
        event.input.value = ""

        if user_text.startswith("/"):
            await self.processar_comando(user_text)
            return

        # 1. Cria e monta a mensagem do usuário
        user_msg = Static(f"[bold #00ff94]user@makise-lab:~$:[/bold #00ff94] {user_text}", classes="msg_user")
        await container.mount(user_msg)
        container.scroll_end(animate=False)

        # 2. Cria o componente isolado para a resposta da Amadeus
        prefix = "[bold #ff0000]Amadeus:[/bold #ff0000] "
        amadeus_msg = Static(prefix, classes="msg_amadeus")
        await container.mount(amadeus_msg)

        spinner_task = asyncio.create_task(self.run_spinner(status))
        start_time = time.perf_counter()

        try:
            current_response = prefix

            # 3. Stream: Atualizamos APENAS a mensagem da Amadeus, não a tela toda!
            async for chunk in falar(user_text):
                if not spinner_task.done():
                    spinner_task.cancel()
                    status.update("")

                current_response += chunk
                amadeus_msg.update(current_response)

                # Mantém a tela rolando para baixo suavemente
                container.scroll_end(animate=False)

            # 4. Finaliza com a latência em um bloco separado
            latency = time.perf_counter() - start_time
            await container.mount(
                Static(f"[dim #555555]Response latency: {latency:.3f}s[/dim #555555]", classes="msg_info"))
            container.scroll_end(animate=False)

        except Exception as e:
            if not spinner_task.done():
                spinner_task.cancel()
            status.update("[bold red]Erro crítico no sistema![/bold red]")
            await container.mount(Static(f"[bold red]ERRO:[/bold red] {str(e)}", classes="msg_info"))
            container.scroll_end(animate=False)


if __name__ == "__main__":
    app = AmadeusKurisu()
    app.run()