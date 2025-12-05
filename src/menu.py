from tkinter import Tk, Menu, Toplevel, Frame, Text, Scrollbar, messagebox
from utils.assets_loader import load_logs
from config.config import Config


class MenuUI:
    def __init__(self, root: Tk) -> None:
        self.root = root


    def render(self) -> None:
        menu = Menu(self.root)
        self.root.config(menu=menu)

        filemenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Log", command=self.show_logs)
        filemenu.add_command(label="Exit", command=self.root.quit)

        helpmenu = Menu(menu, tearoff=False)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=self.show_about)


    def show_about(self) -> None:
        messagebox.showinfo("About", "YouTube comments remover. Purposed to remove comments related to online gambling. Provided 2 options: Manual and Use AI removal.")


    def show_logs(self) -> None:
        logs_root = Toplevel(self.root)
        logs_root.geometry(f"{Config.LOG_WINDOW_WIDTH}x{Config.LOG_WINDOW_HEIGHT}")
        logs_root.title(Config.LOG_WINDOW_TITLE)
        logs_root.resizable(False, False)

        main_frame = Frame(logs_root)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        main_frame.grid_columnconfigure(0, weight=1)

        self.logs_text = Text(main_frame, wrap="word", state="disabled")
        self.logs_text.grid(row=0, column=0, sticky="nsew")

        y_scroll = Scrollbar(main_frame, orient="vertical", command=self.logs_text.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.logs_text.config(yscrollcommand=y_scroll.set)
        
        self._load_logs()
    
    
    def _load_logs(self) -> None:
        logs = load_logs()
        
        self.logs_text.config(state="normal")
        self.logs_text.delete("1.0", "end")
        
        if logs is None:
            self.logs_text.insert("1.0", "No log file found.")

        else:
            self.logs_text.insert("1.0", logs)
        
        self.logs_text.config(state="disabled")
