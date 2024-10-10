import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re


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
    import os
    import tempfile
    
    # Crear una carpeta temporal
    temp_dir = tempfile.mkdtemp()
    print(f"Carpeta temporal creada: {temp_dir}")
    
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
            else:
                print(f"Error al descargar {pdf_url}. Código de estado: {response.status_code}")
        except Exception as e:
            print(f"Error al descargar {pdf_url}: {str(e)}")
    
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
    
else:
    print(f'Acceso no permitido por robots.txt para {url}')


    