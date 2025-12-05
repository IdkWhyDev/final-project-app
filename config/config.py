import sys
from pathlib import Path

class Config:
    @staticmethod
    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS) / relative_path
        return Path(relative_path)

    LOGO_PATH = resource_path("assets/favicon.ico")
    LOGS_PATH = resource_path("assets/logs.log")
    MODEL_PATH = resource_path("assets/model.pkl")
    
    MAIN_WINDOW_WIDTH = 400
    MAIN_WINDOW_HEIGHT = 500
    MAIN_WINDOW_TITLE = "YouTube Comments Remover"
    
    LOG_WINDOW_WIDTH = 600
    LOG_WINDOW_HEIGHT = 400
    LOG_WINDOW_TITLE = "Log(s)"
    
    REMOVE_CONFIRMATION_WINDOW_WIDTH = 600
    REMOVE_CONFIRMATION_WINDOW_HEIGHT = 400
    REMOVE_CONFIRMATION_WINDOW_TITLE = "Confirm Removal"
    
    SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    VIDEO_ID_PATTERN = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    COMMENT_ID_PATTERN = r"Ug[\w-]+"