@echo off
setlocal
py -3 -m venv .venv
call .venv\Scripts\python -m pip install --upgrade pip
call .venv\Scripts\python -m pip install -r requirements.txt
call .venv\Scripts\python -m robot_voice.scripts.bootstrap_defaults
echo setup complete
