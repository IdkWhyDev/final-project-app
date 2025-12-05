import subprocess
from tkinter import Tk, Frame, Label


def get_ping() -> str:
    try:
        output = subprocess.check_output("ping -n 1 console.cloud.google.com", shell=True).decode()
        return output.split("time=")[1].split("ms")[0] + " ms"
    except:
        return "Disconnected"


class FooterUI:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.ping_label = None


    def render(self) -> None:
        frame = Frame(self.root)
        frame.pack(fill="both", expand=True)

        Label(frame, text="@rifqiansharir2025", font=("Arial", 8), fg="gray").pack(side='left', padx=5)

        self.ping_label = Label(frame, text="Checking...", font=("Arial", 8))
        self.ping_label.pack(side='right', padx=5)

        self.show_ping()


    def show_ping(self) -> None:
        ms = get_ping()
        self.ping_label.config(text=ms)
        self.root.after(1000, self.show_ping)
