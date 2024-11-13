#!/bin/sh
echo "Iniciando sincronización..." >> output.txt
date >> output.txt
git pull >> output.txt 2>&1
echo "Activando entorno virtual..." >> output.txt
source .venv/bin/activate
echo "Ejecutando main.py..." >> output.txt
python main.py >> output.txt 2>&1
echo "Agregando cambios..." >> output.txt
git add . >> output.txt 2>&1
echo "Commit de cambios..." >> output.txt
git commit -m "sync_$(date +%Y%m%d)" >> output.txt 2>&1
echo "Enviando cambios..." >> output.txt
git push >> output.txt 2>&1
echo "Sincronización completada." >> output.txt
