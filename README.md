# Final Project: YouTube Comments Remover with AI Powered Online Gambling Detection (App)

## Stack:
1. Runtime:
   - Python 3.13
   - Jupyter Notebook
2. Machine Learning:
   - scikit-learn
   - joblib
   - mlflow
3. Google Integration:
   - google-genai
   - google-auth-oauthlib
   - google-api-python-client
4. Application Layer:
   - tkinter
5. Deployment:
   - PyInstaller (app bundler)
6. Utility:
   - watchdog

## Prerequisites:
1. None.

## Setup:
1. Clone repo: `git clone https://github.com/IdkWhyDev/final-project-app.git`
2. Change directory: `cd final-project-app`
3. Setup venv: `py -3.13 -m venv .venv` and activate it `.venv\Scripts\activate`
4. Install requirements: `pip install --upgrade requirements.txt` and `pip install -r requirements.txt`

## Run:
1. Retrieve model: `python model_retriever.py`
2. Run app: `python app.py` or with auto reload: `watchmedo auto-restart --recursive --pattern="*.py" -- .venv/Scripts/python.exe app.py`
3. Build executable (.exe): `pyinstaller app_builder.spec`