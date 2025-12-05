import threading
import re
from typing import Callable, List, Dict, Optional
from tkinter import Tk, LabelFrame, Frame, Entry, Button, Scrollbar, StringVar, messagebox, Menu
from tkinter import ttk
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
from config.config import Config
from utils.logger import logger


class CommentsLoaderSection:
    def __init__(self, root: Tk, youtube_getter: Callable[[], Optional[Resource]]) -> None:
        self.root = root
        self.youtube_getter = youtube_getter
        self.video_url = StringVar()

        self.comments = None

    
    def render(self) -> None:
        main_frame = LabelFrame(self.root, text="Load Comment(s)")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        entry = Entry(main_frame, textvariable=self.video_url)
        entry.grid(row=0, column=0, padx=5, pady=(0,5), sticky="ew")
        entry.insert(0, "*www.youtube.com")

        Button(main_frame, text="Load", command=self.start_load, width=8).grid(row=0, column=1, padx=5, pady=(0,5))

        child_frame = Frame(main_frame)
        child_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,5), sticky="nsew")
        child_frame.grid_columnconfigure(0, weight=1)
        child_frame.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(child_frame, columns=("id", "author", "text"), show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.heading("id", text="Id")
        self.tree.heading("author", text="Author")
        self.tree.heading("text", text="Text")
        self.tree.column("id", width=80)
        self.tree.column("author", width=80)
        self.tree.column("text", width=150)

        scrollbar = Scrollbar(child_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns") 
        self.tree.config(yscrollcommand=scrollbar.set)

        self.copy_popup = Menu(self.root, tearoff=0)
        self.copy_popup.add_command(label="Copy", command=self.copy_value)
        self.tree.bind("<Button-3>", self.on_right_click)


    def start_load(self) -> None:
        youtube = self.youtube_getter()
        if youtube is None:
            messagebox.showerror("Error", "Authenticate first!")
            return
        
        match = re.search(Config.VIDEO_ID_PATTERN, self.video_url.get())
        if not match:
            messagebox.showerror("Error", "Enter a valid YouTube URL!")
            return
        video_id = match.group(1)
        
        threading.Thread(
            target=self._load_service, 
            kwargs={"youtube": youtube, "video_id": video_id}, 
            daemon=True
        ).start()


    def _load_service(self, youtube: Resource, video_id: str) -> None:
        try:
            comments = []
            next_page = None
            
            while True:
                response = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    pageToken=next_page
                ).execute()

                for item in response.get("items", []):
                    snippet = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "id": item["id"],
                        "author": snippet["authorDisplayName"],
                        "text": snippet["textOriginal"]
                    })

                next_page = response.get("nextPageToken")
                if not next_page:
                    break
              
            self.root.after(0, lambda: self._on_load_success(comments))

        except HttpError as e:
            self.root.after(0, lambda err=e: self._on_http_error(err))
            
        except Exception as e:
            self.root.after(0, lambda err=e: self._on_load_error(err))


    def _on_load_success(self, comments: List[Dict[str, str]]) -> None:
        if comments:
            self.comments = comments        # Update global scope for getter.
            self.render_comments(comments)
            
            logger(f"Loaded {len(comments)} comment(s).", 'INFO')
            messagebox.showinfo("Success", f"Loaded {len(comments)} comment(s).")

        else:
            messagebox.showinfo("Info", "No comment found.")
            return

    def _on_http_error(self, err: Exception) -> None:
        logger(f"Failed to load comments: {err}", "ERROR")
        messagebox.showerror("Error", f"Failed to load comments: {err}")
        
    def _on_load_error(self, err: Exception) -> None:
        logger(f"An unexpected error occurred: {err}", "ERROR")
        messagebox.showerror("Error", f"An unexpected error occurred: {err}")


    def render_comments(self, comments: List[Dict[str, str]]) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)

        for comment in comments:
            self.tree.insert("", "end", values=(comment["id"], comment["author"], comment["text"]))
           
 
    def on_right_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return
        
        col = self.tree.identify_column(event.x)

        self.tree.selection_set(row_id)
        col_index = int(col.replace("#", "")) - 1

        values = self.tree.item(row_id, "values")
        self.selected_cell_value = values[col_index]

        self.copy_popup.tk_popup(event.x_root, event.y_root)


    def copy_value(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.selected_cell_value)
        self.root.update()

    
    def get_comments(self) -> Optional[List[Dict[str, str]]]:
        return self.comments
