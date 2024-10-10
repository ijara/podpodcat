import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import os
import tempfile

def scrape_page_for_pdf(url):
    # Realizar la solicitud HTTP
    response = requests.get(url)
    pdf_urls = []

    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Verificar si el acceso está permitido según robots.txt
        if is_allowed_by_robots(url):
            # Parsear el contenido HTML de la página con BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=lambda href: href and href.lower().endswith('.pdf'))
            
            # Recopilar URLs de PDF
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
    # Get the base URL
    base_url = urlparse(url).scheme + '://' + urlparse(url).netloc

    # Get the robots.txt URL
    robots_url = urljoin(base_url, '/robots.txt')

    try:
        # Fetch the robots.txt content
        robots_content = requests.get(robots_url).text

        # Check if the User-agent is allowed to access the given URL
        return 'User-agent: *\nDisallow:' not in robots_content

    except requests.exceptions.RequestException:
        # If there is an error fetching robots.txt, assume it's allowed
        return True
def descargar_pdfs(pdf_urls):
    # Crear una carpeta temporal
    temp_dir = tempfile.mkdtemp()
    print(f"Carpeta temporal creada: {temp_dir}")
    
    # Variable para pruebas
    modo_prueba = True
    
    # Descargar los PDFs
    for i, pdf_url in enumerate(pdf_urls):
        try:
            response = requests.get(pdf_url)
            if response.status_code == 200:
                # Generar un nombre de archivo único
                filename = f"documento_{i+1}.pdf"
                filepath = os.path.join(temp_dir, filename)
                
                # Guardar el archivo PDF
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"PDF descargado: {filename}")
                
                # Si estamos en modo de prueba, solo descargamos un PDF
                if modo_prueba:
                    break
            else:
                print(f"Error al descargar {pdf_url}. Código de estado: {response.status_code}")
        except Exception as e:
            print(f"Error al descargar {pdf_url}: {str(e)}")
    
    if modo_prueba:
        print("Modo de prueba: Se ha descargado solo un PDF.")
    else:
        print(f"Todos los PDFs han sido descargados en: {temp_dir}")
    return temp_dir




##start
# URL de la página que quieres hacer scraping
url = 'https://www.diariooficial.interior.gob.cl/edicionelectronica/index.php?date=09-10-2024&edition=43969'

if is_allowed_by_robots(url):
    pdf_urls = scrape_page_for_pdf(url)
    # Llamar a la función para descargar los PDFs
    carpeta_temporal = descargar_pdfs(pdf_urls)
    print(f"Los PDFs se han descargado en: {carpeta_temporal}")
    ##tomar el listado de pdf y cargarlos en gemini

    
    # Configurar la API de Gemini
    import os
    from dotenv import load_dotenv
    import io
    

    # Cargar variables de entorno desde el archivo .env
    load_dotenv()

    # Obtener la API key desde las variables de entorno
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    
    # Función para cargar un PDF a Gemini
    def cargar_pdf_a_gemini(ruta_pdf):
        try:
            with open(ruta_pdf, 'rb') as archivo:
                contenido_pdf = archivo.read()
            # Convertir el contenido del PDF a texto
            from pypdf import PdfReader
            
            pdf_reader = PdfReader(io.BytesIO(contenido_pdf))
            texto_pdf = ""
            for pagina in pdf_reader.pages:
                texto_pdf += pagina.extract_text()
            
            print(f"Texto extraído del PDF: {os.path.basename(ruta_pdf)}")
            # Crear un modelo de Gemini para procesar PDFs
            modelo = genai.GenerativeModel('gemini-1.5-flash')
            
            # Cargar el PDF al modelo
            respuesta = modelo.generate_content(texto_pdf)
            
            print(f"PDF cargado exitosamente: {os.path.basename(ruta_pdf)}")
            return respuesta
        except Exception as e:
            print(f"Error al cargar el PDF {os.path.basename(ruta_pdf)}: {str(e)}")
            return None
    
    # Cargar todos los PDFs de la carpeta temporal a Gemini
    respuestas_gemini = []
    for archivo in os.listdir(carpeta_temporal):
        if archivo.endswith('.pdf'):
            ruta_completa = os.path.join(carpeta_temporal, archivo)
            respuesta = cargar_pdf_a_gemini(ruta_completa)
            if respuesta:
                respuestas_gemini.append(respuesta)
    
    print(f"Se han cargado {len(respuestas_gemini)} PDFs a Gemini.")
    
    # Leer el contenido del archivo prompt.txt
    with open('prompt.txt', 'r', encoding='utf-8') as archivo_prompt:
        instrucciones_podcast = archivo_prompt.read()
    
    # Generar la conversación estilo podcast
    modelo_conversacion = genai.GenerativeModel('gemini-pro')
    
    # Combinar la información de los PDFs y las instrucciones
    contexto_completo = "\n".join([str(resp) for resp in respuestas_gemini]) + "\n\n" + instrucciones_podcast
    
    conversacion_podcast = modelo_conversacion.generate_content(contexto_completo)
    
    print("Conversación estilo podcast generada:")
    print(conversacion_podcast.text)
    ## luego generar una conversacion tambien usando gemini
    ## finalmente pasar esa conversacion a tts tambien usando gemini
else:
    print(f'Acceso no permitido por robots.txt para {url}')


    