import time
import asyncio
from textual.app import App
from textual.widgets import Header, Footer, RichLog, Input, Static
from textual.containers import Vertical

from kurisu.brain_func.core import falar


class AmadeusKurisu(App):
    CSS = """
    Screen { background: #0a0a1a; }

    #chat_log { 
        height: 1fr; 
        border: ascii #FF003C; 
        background: #0D0D0D; 
        padding: 1;
    }

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
        yield RichLog(id="chat_log", markup=True)
        yield Static(id="status_bar")
        yield Input(placeholder="user@makise-lab:~$")
        yield Footer()

    def on_mount(self):
        log = self.query_one("#chat_log", RichLog)
        GOLD = "#FFD700"

        banner = rf"""[bold {GOLD}]
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

        log.write(banner)
        log.write("["
                  "bold #ff7700]>>> Sistema Amadeus online...[/bold #ff7700]\n")

    async def run_spinner(self, status_widget):
        spinner = ["|", "/", "-", "\\"]
        i = 0
        while True:
            status_widget.update(f"[bold #ff7700]{spinner[i % 4]} Kurisu is Thinking...")
            i += 1
            await asyncio.sleep(0.1)

    async def on_input_submitted(self, event: Input.Submitted):
        user_text = event.value
        if not user_text: return

        log = self.query_one("#chat_log", RichLog)
        status = self.query_one("#status_bar", Static)

        log.write(f"[bold #00ff94]user@makise-lab:~$:[/bold #00ff94] {user_text}")
        event.input.value = ""

        spinner_task = asyncio.create_task(self.run_spinner(status))

        start_time = time.perf_counter()

        try:
            resposta = await falar(user_text)
            latency = time.perf_counter() - start_time

            spinner_task.cancel()
            status.update("")

            log.write(f"[bold #ff0000]Amadeus:[/bold #ff0000] {resposta}")
            log.write(f"[dim #555555]Response latency: {latency:.3f}s[/dim #555555]\n")

        except Exception as e:
            spinner_task.cancel()
            status.update("[bold red]Erro crítico no sistema![/bold red]")
            log.write(f"[bold red]ERRO:[/bold red] {str(e)}")


if __name__ == "__main__":
    app = AmadeusKurisu()
    app.run()