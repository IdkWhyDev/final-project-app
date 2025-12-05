import threading
import re
from typing import Callable, List, Dict, Optional
from tkinter import Tk, Toplevel, StringVar, BooleanVar
from tkinter import Frame, LabelFrame, Entry, Button, Checkbutton, Menu, Scrollbar
from tkinter import messagebox
from tkinter import ttk
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
from sklearn.base import BaseEstimator
from config.config import Config
from utils.comment_normalizer import normalize_comment
from utils.logger import logger


class CommentsRemoverSection:
    def __init__(self, 
                 root: Tk, 
                 model: Optional[BaseEstimator], 
                 youtube_getter: Callable[[], Optional[Resource]],
                 comments_getter: Callable[[], Optional[List[Dict[str, str]]]]) -> None:
        self.root = root
        self.model = model
        self.youtube_getter = youtube_getter
        self.comments_getter = comments_getter
        self.target_comment_id = StringVar()                    
        self.enable_ban_author = BooleanVar(value=False)
        self.enable_ai_assisted = BooleanVar(value=False)

        self.flagged_comments = None


    def render(self) -> None:
        main_frame = LabelFrame(self.root, text="Remove comment(s)")
        main_frame.pack(fill="x", padx=5, pady=(5,0))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        self.entry = Entry(main_frame, textvariable=self.target_comment_id)
        self.entry.grid(row=0, column=0, padx=5, pady=(0,5), sticky='ew')
        self.entry.insert(0, "*Id")

        Button(main_frame, text="Remove", command=self.start_remove).grid(row=0, column=1, padx=5, pady=(0,5))
        
        child_frame = Frame(main_frame)
        child_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        
        Checkbutton(child_frame, text="Ban author", variable=self.enable_ban_author).grid(row=0, column=0, sticky='nw')
        Checkbutton(child_frame, text="AI assisted (remove online gambling)", variable=self.enable_ai_assisted, command=self.disable_comments_entry).grid(row=1, column=0, sticky='nw')        

    
    def start_remove(self) -> None:
        youtube = self.youtube_getter()
        if youtube is None:
            messagebox.showerror("Error", "Authenticate first!")
            return
        
        if not self.enable_ai_assisted.get():
            match = re.search(Config.COMMENT_ID_PATTERN, self.target_comment_id.get())
            if not match:
                messagebox.showerror("Error", "Enter a valid comment id!")
                return
            comment_id = match.group(0)
            
            threading.Thread(
                target=self._manual_remove_service, 
                kwargs={"youtube": youtube, "comment_id": comment_id},
                daemon=True
            ).start()

        else:
            comments = self.comments_getter()
            if comments is None or self.model is None:
                return

            threading.Thread(
                target=self._ai_assisted_remove_service, 
                kwargs={"youtube": youtube, "model": self.model, "comments": comments},
                daemon=True
            ).start()


    def _manual_remove_service(self, youtube: Resource, comment_id: str) -> None:   
        try:
            youtube.comments().setModerationStatus(
                id=comment_id,
                moderationStatus="rejected",
                banAuthor=self.enable_ban_author.get()
            ).execute()
            
            self.root.after(0, lambda: self._on_manual_remove_success(comment_id))
            
        except HttpError as e:
            self.root.after(0, lambda err=e: self._on_http_error(err))
            
        except Exception as e:
            self.root.after(0, lambda err=e: self._on_remove_error(err))
            
    
    def _ai_assisted_remove_service(self, youtube: Resource, model: BaseEstimator, comments: Optional[List[Dict[str, str]]]) -> None:
        comments = self.comments_getter()
        if comments is None or self.model is None:
            return

        try:
            texts = [normalize_comment(c["text"]) for c in comments]
            predictions = model.predict(texts)
            flagged_comments = [comments[i] for i, p in enumerate(predictions) if p == 1]

        except Exception as e:
            self.root.after(0, lambda err=e: self._on_ai_prediction_error(err))

        if not flagged_comments:
            self.root.after(0, lambda: messagebox.showinfo("Info", "No flagged comment to remove."))
            return
        
        self.flagged_comments = flagged_comments        # Send to global scope.
        self.root.after(0, lambda: self.remove_confirmation(youtube))
    

    def remove_confirmation(self, youtube: Resource) -> None:
        self.confirmation_root = Toplevel(self.root)
        self.confirmation_root.geometry(f"{Config.REMOVE_CONFIRMATION_WINDOW_WIDTH}x{Config.REMOVE_CONFIRMATION_WINDOW_HEIGHT}")
        self.confirmation_root.title(Config.REMOVE_CONFIRMATION_WINDOW_TITLE)
        self.confirmation_root.resizable(False, False)
        
        self.confirmation_root.transient(self.root)
        self.confirmation_root.grab_set()
        self.confirmation_root.protocol("WM_DELETE_WINDOW", lambda: self.on_close_confirmation())

        main_frame = Frame(self.confirmation_root)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1) 

        self.tree = ttk.Treeview(main_frame, columns=("id", "author", "text"), show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.heading("id", text="ID")
        self.tree.heading("author", text="Author")
        self.tree.heading("text", text="Text")
        self.tree.column("id", width=150)
        self.tree.column("author", width=150)
        self.tree.column("text", width=300)

        y_scroll = Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.config(yscrollcommand=y_scroll.set)
        
        confirm_frame = Frame(main_frame)
        confirm_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew") 

        confirm_frame.grid_columnconfigure(0, weight=1)
        # confirm_frame.grid_rowconfigure(0, weight=1)
        
        Button(confirm_frame, text="Confirm", command=lambda: self.on_confirm(youtube), width=8).grid(row=0, column=1, pady=5, padx=5)

        self.render_flagged_comments()

        self.confirmation_root.wait_window(self.confirmation_root)


    def on_close_confirmation(self) -> None:
        self.flagged_comments = None
        self.confirmation_root.destroy()
        
    
    def on_confirm(self, youtube: Resource) -> None:
        threading.Thread(
            target=self._ai_assisted_remove_service_2, 
            kwargs={"youtube": youtube},
            daemon=True
        ).start()
    
    def _ai_assisted_remove_service_2(self, youtube: Resource) -> None:
        try:
            for comment in self.flagged_comments:       # Get updated flagged_comments.
                youtube.comments().setModerationStatus(
                    id=comment['id'],
                    moderationStatus="rejected",
                    banAuthor=self.enable_ban_author.get()
                ).execute()
            
            len_flagged_comments = len(self.flagged_comments)
            self.root.after(0, lambda: self._on_ai_assisted_remove_success(len_flagged_comments))
            
        except HttpError as e:
            self.root.after(0, lambda err=e: self._on_http_error(err))
            
        except Exception as e:
            self.root.after(0, lambda err=e: self._on_remove_error(err))

        self.on_close_confirmation()


    def _on_manual_remove_success(self, comment_id: str) -> None:
        logger(f"Removed comment with id: {comment_id}", 'INFO')
        messagebox.showinfo("Success", f"Removed comment with id: {comment_id}")

    def _on_ai_assisted_remove_success(self, len_flagged_comments: int) -> None:
        logger(f"Removed {len_flagged_comments} comments", 'INFO')
        messagebox.showinfo("Success", f"Removed {len_flagged_comments} comments")
        
    def _on_ai_prediction_error(self, err: Exception) -> None:
        logger(f"AI Prediction failed: {err}", 'ERROR')
        messagebox.showerror("Error", f"AI Prediction failed: {err}")

    def _on_http_error(self, err: Exception) -> None:
        logger(f"Failed to remove comments: {err}", "ERROR")
        messagebox.showerror("Error", f"Failed to remove comments: {err}")

    def _on_remove_error(self, err: Exception) -> None:
        logger(f"An unexpected error occurred: {err}", "ERROR")
        messagebox.showerror("Error", f"An unexpected error occurred: {err}")
        

    def render_flagged_comments(self) -> None:
        for flagged_comment in self.flagged_comments:
            self.tree.insert("", "end", iid=flagged_comment["id"], values=(flagged_comment["id"], flagged_comment["author"], flagged_comment["text"]))

        self.cancel_popup = Menu(self.confirmation_root, tearoff=0)
        self.cancel_popup.add_command(label="Cancel", command=lambda: self.cancel_item())
        self.tree.bind("<Button-3>", lambda e: self.on_right_click(e))


    def cancel_item(self) -> None:
        selected = self.tree.selection()
        if selected:
            cid_to_remove = selected[0]
            self.tree.delete(cid_to_remove)
            self.flagged_comments[:] = [c for c in self.flagged_comments if c["id"] != cid_to_remove]


    def on_right_click(self, event) -> None:
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.cancel_popup.tk_popup(event.x_root, event.y_root)


    def disable_comments_entry(self) -> None:
        if self.enable_ai_assisted.get():
            self.entry.config(state="disabled")
        else:
            self.entry.config(state="normal")
