import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import tempfile
import io
from dotenv import load_dotenv
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

def cargar_pdf_a_gemini(ruta_pdf):
    try:
        with open(ruta_pdf, 'rb') as archivo:
            contenido_pdf = archivo.read()
        
        pdf_reader = PdfReader(io.BytesIO(contenido_pdf))
        texto_pdf = "".join(pagina.extract_text() for pagina in pdf_reader.pages)
        
        print(f"Texto extraído del PDF: {os.path.basename(ruta_pdf)}")
        modelo = genai.GenerativeModel('gemini-1.5-flash')
        
        respuesta = modelo.generate_content(texto_pdf)
        
        print(f"PDF cargado exitosamente: {os.path.basename(ruta_pdf)}")
        return respuesta
    except Exception as e:
        print(f"Error al cargar el PDF {os.path.basename(ruta_pdf)}: {str(e)}")
        return None

def main():
    url = 'https://www.diariooficial.interior.gob.cl/edicionelectronica/index.php?date=09-10-2024&edition=43969'

    if is_allowed_by_robots(url):
        pdf_urls = scrape_page_for_pdf(url)
        carpeta_temporal = descargar_pdfs(pdf_urls)
        print(f"Los PDFs se han descargado en: {carpeta_temporal}")

        load_dotenv()
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        respuestas_gemini = []
        for archivo in os.listdir(carpeta_temporal):
            if archivo.endswith('.pdf'):
                ruta_completa = os.path.join(carpeta_temporal, archivo)
                respuesta = cargar_pdf_a_gemini(ruta_completa)
                if respuesta:
                    respuestas_gemini.append(respuesta)
        
        print(f"Se han cargado {len(respuestas_gemini)} PDFs a Gemini.")
        
        with open('prompt.txt', 'r', encoding='utf-8') as archivo_prompt:
            instrucciones_podcast = archivo_prompt.read()
        
        modelo_conversacion = genai.GenerativeModel('gemini-pro')
        
        contexto_completo = "\n".join([str(resp) for resp in respuestas_gemini]) + "\n\n" + instrucciones_podcast
        
        conversacion_podcast = modelo_conversacion.generate_content(contexto_completo)
        
        print("Conversación estilo podcast generada:")
        print(conversacion_podcast.text)
    else:
        print(f'Acceso no permitido por robots.txt para {url}')

if __name__ == "__main__":
    main()