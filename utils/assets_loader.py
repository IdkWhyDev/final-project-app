from typing import Optional
from sklearn.base import BaseEstimator
from joblib import load
from tkinter import messagebox
from config.config import Config
from utils.logger import logger


def load_logs() -> str:
    try:
        with open(Config.LOGS_PATH, "r", encoding="utf-8") as f:
            logs = f.read()
            return logs

    except Exception as e:
        messagebox.showerror("Error", "Logs failed to load.")
        return None


def load_model() -> Optional[BaseEstimator]:
    try:
        model = load(Config.MODEL_PATH)
        logger("Model loaded.", 'INFO')
        return model

    except Exception as e:
        logger(f"Model failed to load: {e}", 'ERROR')
        messagebox.showerror("Error", "Model failed to load.")
        return None
