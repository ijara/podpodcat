#!/bin/sh
cd /home/ijara756/podpodcat/
echo "Iniciando sincronización..." >> /home/ijara756/podpodcat/output.txt
date >> /home/ijara756/podpodcat/output.txt
git pull >> /home/ijara756/podpodcat/output.txt 2>&1
echo "Activando entorno virtual..." >> /home/ijara756/podpodcat/output.txt
source /home/ijara756/podpodcat/.venv/bin/activate
echo "Ejecutando main.py..." >> /home/ijara756/podpodcat/output.txt
/home/ijara756/podpodcat/.venv/bin/python /home/ijara756/podpodcat/main.py >> /home/ijara756/podpodcat/output.txt 2>&1
echo "Agregando cambios..." >> /home/ijara756/podpodcat/output.txt
git add . >> /home/ijara756/podpodcat/output.txt 2>&1
echo "Commit de cambios..." >> /home/ijara756/podpodcat/output.txt
git commit -m "sync_$(date +%Y%m%d)" >> /home/ijara756/podpodcat/output.txt 2>&1
echo "Enviando cambios..." >> /home/ijara756/podpodcat/output.txt
git push >> /home/ijara756/podpodcat/output.txt 2>&1
echo "Sincronización completada." >> /home/ijara756/podpodcat/output.txt
