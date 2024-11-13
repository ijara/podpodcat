*/1 * * * * /bin/sh -c 'git pull && source .venv/bin/activate && python main.py && git add . && git commit -m "sync_$(date +\'%Y%m%d\')" && git push'
