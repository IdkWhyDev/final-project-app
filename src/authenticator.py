import threading
from typing import Optional
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from tkinter import messagebox, StringVar, Tk, LabelFrame, Entry, Button, filedialog
from config.config import Config
from utils.logger import logger


class AuthSection:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.credential_file_path = StringVar()
        
        self.youtube = None


    def render(self) -> None:
        main_frame = LabelFrame(self.root, text="Authentication")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        entry = Entry(main_frame, textvariable=self.credential_file_path)
        entry.grid(row=0, column=0, padx=5, pady=(0,5), sticky='ew')
        entry.insert(0, "*client_secret.json")

        Button(main_frame, text="Browse", command=self.browse_credential, width=8).grid(row=0, column=1, padx=5, pady=(0,5))
        Button(main_frame, text="Auth", command=self.start_auth, width=8).grid(row=0, column=2, padx=5, pady=(0,5))


    def browse_credential(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file_path:
            self.credential_file_path.set(file_path)


    def start_auth(self) -> None:
        credential_file_path = self.credential_file_path.get()
        
        if not credential_file_path:
            messagebox.showerror("Error", "Upload credential file first!")
            return
        
        threading.Thread(
            target=self._auth_service, 
            kwargs={"credential_file_path": credential_file_path}, 
            daemon=True
        ).start()


    def _auth_service(self, credential_file_path) -> None:
        try:
            flow = InstalledAppFlow.from_client_secrets_file(credential_file_path, Config.SCOPES)
            credentials = flow.run_local_server(port=0)
            self.youtube = build("youtube", "v3", credentials=credentials)
            
            file_name = Path(credential_file_path).name
            self.root.after(0, lambda: self._on_auth_success(file_name))

        except Exception as e:
            self.root.after(0, lambda err=e: self._on_auth_error(err))
        
    
    def _on_auth_success(self, file_name: str) -> None:
        logger(f"Authentication complete with: {file_name}", "INFO")
        messagebox.showinfo("Success", "Authentication complete.")    
    
    def _on_auth_error(self, err: Exception) -> None:
        logger(f"Authentication error: {err}", "ERROR")
        messagebox.showerror("Error", f"Authentication error: {err}")


    def get_youtube(self) -> Optional[Resource]:
        return self.youtube
