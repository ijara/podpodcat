@echo off
call .venv\Scripts\activate.bat
python main.py
git add .
git commit -m "sync_%date:~0,8%"
git push
