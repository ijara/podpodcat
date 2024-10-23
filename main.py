import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import tempfile
import io
from pypdf import PdfReader
import openai
from openai import OpenAI

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

def explicar_proceso_a_chatgpt():
    print("Explicando el proceso a ChatGPT...")
    client = OpenAI(api_key=openai.api_key)  # Asegúrate de que la clave API esté configurada
    instrucciones = """
   Te entregare informacion, quiero que vayas agregando esta informacion hasta que indique el comando [end-info].
    """
    respuesta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente especializado en análisis de documentos legales."},
            {"role": "user", "content": instrucciones}
        ]
    )
    # Actualiza esta línea para acceder correctamente al contenido de la respuesta
    print("Respuesta de ChatGPT:")
    print(respuesta.choices[0].message.content)  # Cambia esto para acceder al contenido de la respuesta

def cargar_pdf_a_chatgpt(ruta_pdf):
    print(f"Intentando cargar PDF a ChatGPT: {os.path.basename(ruta_pdf)}")
    try:
        with open(ruta_pdf, 'rb') as archivo:
            contenido_pdf = archivo.read()
        
        pdf_reader = PdfReader(io.BytesIO(contenido_pdf))
        texto_pdf = "".join(pagina.extract_text() for pagina in pdf_reader.pages)
        
        print(f"Texto extraído del PDF: {os.path.basename(ruta_pdf)}")
        
        # Limitar el texto a un tamaño manejable
        max_tokens = 4096  # Ajusta este valor según el modelo
        if len(texto_pdf.split()) > max_tokens:
            texto_pdf = " ".join(texto_pdf.split()[:max_tokens])  # Truncar el texto

        respuesta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "genera un newsletter, que separe esta informacion de la siguiente forma: cada cve debe ser explicado en base a la documentacion entregada"},
                {"role": "user", "content": texto_pdf}
            ]
        )
        
        print(f"PDF analizado exitosamente: {os.path.basename(ruta_pdf)}")
        return respuesta.choices[0].message.content
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
        
        with open('prompt.txt', 'r', encoding='utf-8') as archivo_prompt:
            instrucciones = archivo_prompt.read()
        print("Respuestas de ChatGPT:")
        for respuesta in respuestas_chatgpt:
            print(respuesta)
        contexto_completo = "\n".join(respuestas_chatgpt) + "\n\n" + instrucciones
        
        client = OpenAI(api_key=openai.api_key)  # Asegúrate de que la clave API esté configurada
        respuesta_final = client.chat.completions.create(  # Cambia openai por client
            model="gpt-3.5-turbo",
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
