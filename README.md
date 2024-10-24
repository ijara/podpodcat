# podpodcat
## commands
- commands
	- sudo apt-get update
	- sudo apt-get install  python3 python3-pip ffmpeg
    - sudo apt install python3.12-venv
    - python3 -m venv .venv
	- source .venv/bin/activate
    - pip install podcastfy
	- pip freeze > requirements.txt
	- pip install -r requirements.txt

## to do
- rename config.py.bak to config.py

## things to remember
- buscar la forma de que el mensaje de commit sea autogenerado por llm
- reestructurar la consulta
	- idea! verificar si es posible que la informacion que ya haya sido subida, sea recordada, en base a eso consultar por un resumen, sin tener que volver a cargar toda la info
	- quitar puntos innecesarios como alzamientos, presuntas muertes, temas no relevantes con el objetivo principal