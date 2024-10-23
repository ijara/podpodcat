import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import tempfile
import io
from pypdf import PdfReader
import openai
from openai import OpenAI
import datetime  # Añadir esta línea al inicio del archivo

# Variable global para el modelo
modelo_global = "gpt-3.5-turbo"

def scrape_page_for_pdf(url):
    print(f"Intentando acceder a la página: {url}")
    response = requests.get(url)
    pdf_urls = []

    if response.status_code == 200:
        print(f"Acceso exitoso a la página. Código de estado: {response.status_code}")
        if is_allowed_by_robots(url):
            print("Verificando permisos de robots.txt...")
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=lambda href: href and href.lower().endswith('.pdf'))
            
            for link in links:
                pdf_url = urljoin(url, link.get('href'))
                pdf_urls.append(pdf_url)
            
            print(f"Se encontraron {len(pdf_urls)} enlaces a archivos PDF.")
        else:
            print(f'Acceso no permitido por robots.txt para {url}')
    else:
        print(f'Error al hacer la solicitud HTTP. Código de estado: {response.status_code}')
    
    return pdf_urls

def is_allowed_by_robots(url):
    print(f"Verificando permisos de robots.txt para {url}...")
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    robots_url = urljoin(base_url, '/robots.txt')

    try:
        robots_content = requests.get(robots_url).text
        return 'User-agent: *\nDisallow:' not in robots_content
    except requests.exceptions.RequestException:
        print(f"Error al acceder a robots.txt para {url}. Se asume permiso.")
        return True

def descargar_pdfs(pdf_urls, modo_prueba=False):
    print("Creando carpeta temporal...")
    temp_dir = tempfile.mkdtemp()
    print(f"Carpeta temporal creada: {temp_dir}")
    
    for i, pdf_url in enumerate(pdf_urls):
        print(f"Intentando descargar PDF: {pdf_url}")
        try:
            response = requests.get(pdf_url)
            if response.status_code == 200:
                filename = f"documento_{i+1}.pdf"
                filepath = os.path.join(temp_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"PDF descargado: {filename}")
                
                if modo_prueba:
                    print("Modo de prueba activado. Se detendrá después de descargar un PDF.")
                    break
            else:
                print(f"Error al descargar {pdf_url}. Código de estado: {response.status_code}")
        except Exception as e:
            print(f"Error al descargar {pdf_url}: {str(e)}")
    
    print("Modo de prueba: Se ha descargado solo un PDF." if modo_prueba else f"Todos los PDFs han sido descargados en: {temp_dir}")
    return temp_dir

def cargar_pdf_a_chatgpt(ruta_pdf):
    print(f"Intentando cargar PDF a ChatGPT: {os.path.basename(ruta_pdf)}")
    try:
        with open(ruta_pdf, 'rb') as archivo:
            contenido_pdf = archivo.read()
        
        pdf_reader = PdfReader(io.BytesIO(contenido_pdf))
        texto_pdf = "".join(pagina.extract_text() for pagina in pdf_reader.pages)
        
        print(f"Texto extraído del PDF: {os.path.basename(ruta_pdf)}")
        
        # Dividir el texto en partes manejables
        max_tokens = 4096  # Ajusta este valor según el modelo
        partes_texto = [texto_pdf[i:i+max_tokens] for i in range(0, len(texto_pdf), max_tokens)]
        
        respuestas = []
        for parte in partes_texto:
            respuesta = openai.chat.completions.create(
                model=modelo_global,  # Usando la variable global para el modelo
                messages=[
                    {"role": "system", "content": "explica cada cve en base a la documentacion entregada"},
                    {"role": "user", "content": parte}
                ]
            )
            
            respuestas.append(respuesta.choices[0].message.content)
        
        print(f"PDF analizado exitosamente: {os.path.basename(ruta_pdf)}")
        return respuestas
    except Exception as e:
        print(f"Error al analizar el PDF {os.path.basename(ruta_pdf)}: {str(e)}")
        return None

def main():
    url = 'https://www.diariooficial.interior.gob.cl/edicionelectronica/'

    print(f"Intentando acceder a la URL: {url}")
    if is_allowed_by_robots(url):
        print("Acceso permitido por robots.txt. Continuando...")
        pdf_urls = scrape_page_for_pdf(url)
        carpeta_temporal = descargar_pdfs(pdf_urls)
        print(f"Los PDFs se han descargado en: {carpeta_temporal}")

        #explicar_proceso_a_chatgpt()
        respuestas_chatgpt = []
        for archivo in os.listdir(carpeta_temporal):
            if archivo.endswith('.pdf'):
                ruta_completa = os.path.join(carpeta_temporal, archivo)
                respuesta = cargar_pdf_a_chatgpt(ruta_completa)
                if respuesta:
                    respuestas_chatgpt.append(respuesta)
        
        print(f"Se han analizado {len(respuestas_chatgpt)} PDFs con ChatGPT.")
        print("Respuestas de ChatGPT:")
        for respuesta in respuestas_chatgpt:
            print(respuesta)
        
        # Asegúrate de que respuestas_chatgpt sea una lista de cadenas
        # Si respuestas_chatgpt es una lista de listas, aplana la lista
        if isinstance(respuestas_chatgpt, list) and all(isinstance(item, list) for item in respuestas_chatgpt):
            respuestas_chatgpt = [item for sublist in respuestas_chatgpt for item in sublist]  # Aplanar la lista

        contexto_completo = "\n".join(respuestas_chatgpt)  # Ahora debería funcionar correctamente
        
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d")  # Cambiar a datetime.datetime
        directorio_diario = "daily"
        nombre_archivo = f"newsletter_{fecha_actual}.txt"
        ruta_completa_archivo = os.path.join(directorio_diario, nombre_archivo)
        
        if not os.path.exists(directorio_diario):
            os.makedirs(directorio_diario)
        
        with open(ruta_completa_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(contexto_completo)
        
        print(f"Contexto completo guardado en: {ruta_completa_archivo}")
        client = OpenAI(api_key=openai.api_key)  # Asegúrate de que la clave API esté configurada
        respuesta_final = client.chat.completions.create(  # Cambia openai por client
            model=modelo_global,  # Usando la variable global para el modelo
            messages=[
                {"role": "system", "content": "genera un newsletter, que separe esta informacion de la siguiente forma: cada cve debe ser explicado en base a la documentacion entregada"},
                {"role": "user", "content": contexto_completo}
            ]
        )
        
        # Acceder al contenido de la respuesta correctamente
        contenido_respuesta_final = respuesta_final.choices[0].message.content
        print("Resumen generado:")
        print(contenido_respuesta_final)
    else:
        print(f'Acceso no permitido por robots.txt para {url}')

if __name__ == "__main__":
    from config import OPENAI_API_KEY  # Importa la clave API desde un archivo de configuración
    openai.api_key = OPENAI_API_KEY  # Usa la variable importada para la API key de OpenAI
    main()
