from tkinter import Tk
from tkinter import *
from utils.assets_loader import load_model
from src.menu import MenuUI
from src.authenticator import AuthSection
from src.comments_loader import CommentsLoaderSection
from src.comments_remover import CommentsRemoverSection
from src.footer import FooterUI
from config.config import Config


class App:
    def __init__(self):
        self.root = Tk()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - Config.MAIN_WINDOW_WIDTH + 1300) // 2
        y = (screen_height - Config.MAIN_WINDOW_HEIGHT) // 2
        self.root.geometry(f"{Config.MAIN_WINDOW_WIDTH}x{Config.MAIN_WINDOW_HEIGHT}+{x}+{y}")
        self.root.iconbitmap(Config.LOGO_PATH)
        self.root.title(Config.MAIN_WINDOW_TITLE)
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        

    def run_app(self):
        model = load_model()
        menu_ui = MenuUI(self.root)
        menu_ui.render()
        auth_section = AuthSection(self.root)
        auth_section.render()
        comments_loader = CommentsLoaderSection(self.root, auth_section.get_youtube)
        comments_loader.render()
        comments_remover = CommentsRemoverSection(self.root, model, auth_section.get_youtube, comments_loader.get_comments)
        comments_remover.render()
        footer = FooterUI(self.root)
        footer.render()
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run_app()
