*/1 * * * * /bin/sh -c 'source .venv/bin/activate && python main.py && git add . && git commit -m "sync_$(date +\'%Y%m%d\')" && git push'
