import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import tempfile
import io
import ollama
from pypdf import PdfReader

def scrape_page_for_pdf(url):
    response = requests.get(url)
    pdf_urls = []

    if response.status_code == 200:
        if is_allowed_by_robots(url):
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
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    robots_url = urljoin(base_url, '/robots.txt')

    try:
        robots_content = requests.get(robots_url).text
        return 'User-agent: *\nDisallow:' not in robots_content
    except requests.exceptions.RequestException:
        return True

def descargar_pdfs(pdf_urls, modo_prueba=True):
    temp_dir = tempfile.mkdtemp()
    print(f"Carpeta temporal creada: {temp_dir}")
    
    for i, pdf_url in enumerate(pdf_urls):
        try:
            response = requests.get(pdf_url)
            if response.status_code == 200:
                filename = f"documento_{i+1}.pdf"
                filepath = os.path.join(temp_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"PDF descargado: {filename}")
                
                if modo_prueba:
                    break
            else:
                print(f"Error al descargar {pdf_url}. Código de estado: {response.status_code}")
        except Exception as e:
            print(f"Error al descargar {pdf_url}: {str(e)}")
    
    print("Modo de prueba: Se ha descargado solo un PDF." if modo_prueba else f"Todos los PDFs han sido descargados en: {temp_dir}")
    return temp_dir

def explicar_proceso_a_ollama():
    instrucciones = """
    Estás a punto de comenzar un proceso de análisis de documentos oficiales del Diario Oficial de Chile.
    Tu tarea será:
    1. Leer y comprender el contenido de los PDFs descargados.
    2. Identificar información relevante sobre nuevas leyes, decretos o regulaciones.
    3. Resumir los puntos clave de cada documento.    
    Por favor, confirma que has entendido estas instrucciones y estás listo para comenzar el análisis.
    """
    respuesta = ollama.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': instrucciones
        }
    ])
    print("Respuesta de Ollama:")
    print(respuesta['message']['content'])


def cargar_pdf_a_ollama(ruta_pdf):
    try:
        with open(ruta_pdf, 'rb') as archivo:
            contenido_pdf = archivo.read()
        
        pdf_reader = PdfReader(io.BytesIO(contenido_pdf))
        texto_pdf = "".join(pagina.extract_text() for pagina in pdf_reader.pages)
        
        print(f"Texto extraído del PDF: {os.path.basename(ruta_pdf)}")
        
        respuesta = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': texto_pdf
            }
        ])
        
        print(f"PDF incrustado exitosamente: {os.path.basename(ruta_pdf)}")
        return respuesta
    except Exception as e:
        print(f"Error al incrustar el PDF {os.path.basename(ruta_pdf)}: {str(e)}")
        return None

def main():
    url = 'https://www.diariooficial.interior.gob.cl/edicionelectronica/'

    if is_allowed_by_robots(url):
        pdf_urls = scrape_page_for_pdf(url)
        carpeta_temporal = descargar_pdfs(pdf_urls)
        print(f"Los PDFs se han descargado en: {carpeta_temporal}")

        
        explicar_proceso_a_ollama()
        respuestas_ollama = []
        for archivo in os.listdir(carpeta_temporal):
            if archivo.endswith('.pdf'):
                ruta_completa = os.path.join(carpeta_temporal, archivo)
                respuesta = cargar_pdf_a_ollama(ruta_completa)
                if respuesta:
                    respuestas_ollama.append(respuesta)
        
        print(f"Se han cargado {len(respuestas_ollama)} PDFs a Ollama.")
        
        with open('prompt.txt', 'r', encoding='utf-8') as archivo_prompt:
            instrucciones = archivo_prompt.read()
        
        contexto_completo = "\n".join([str(resp) for resp in respuestas_ollama]) + "\n\n" + instrucciones
        
        respuesta = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': instrucciones
            }
        ])
        
        print("Conversación generada:")
        print(respuesta)
    else:
        print(f'Acceso no permitido por robots.txt para {url}')

if __name__ == "__main__":
    main()