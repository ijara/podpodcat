#!/bin/sh
echo "Iniciando sincronización..."
git pull
echo "Activando entorno virtual..."
source .venv/bin/activate
echo "Ejecutando main.py..."
python main.py
if [ $? -eq 1 ]; then
    echo "Agregando cambios..."
    git add .
    echo "Commit de cambios..."
    git commit -m "sync_$(date +%Y%m%d)"
    echo "Enviando cambios..."
    git push
    echo "Sincronización completada."
fi
