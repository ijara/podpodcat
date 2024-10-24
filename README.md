# podpodcat
### ultima version

{% include daily\latest.md %}

## Comandos
- Actualizar el sistema: `sudo apt-get update`
- Instalar Python3, pip y ffmpeg: `sudo apt-get install  python3 python3-pip ffmpeg`
- Instalar el entorno virtual de Python 3.12: `sudo apt install python3.12-venv`
- Crear y activar el entorno virtual: 
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
- Instalar podcastfy: `pip install podcastfy`
- Guardar los requisitos en un archivo: `pip freeze > requirements.txt`
- Instalar los requisitos desde el archivo: `pip install -r requirements.txt`

## Por hacer
- Renombrar `config.py.bak` a `config.py`

## Cosas para recordar
- Buscar la forma de que el mensaje de commit sea autogenerado por llm
- Reestructurar la consulta
	- Verificar si es posible recordar la información ya subida para consultar un resumen, sin tener que volver a cargar toda la información
	- Quitar puntos innecesarios como alzamientos, presuntas muertes, temas no relevantes con el objetivo principal