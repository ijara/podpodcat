#!/bin/sh
source .venv/bin/activate
if python main.py; then
    git add .
    git commit -m "sync_$(date +'%Y%m%d')"
    git push
fi
