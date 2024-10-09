import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re


def scrape_page(url):
    # Realizar la solicitud HTTP
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Verificar si el acceso está permitido según robots.txt
        if is_allowed_by_robots(url):
            # Parsear el contenido HTML de la página con BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=lambda href: href)
            # Mostrar el contenido de links
            print("Enlaces encontrados:")
            if links:
                for link in links:
                    print(link.get('href'))
        else:
            print(f'Acceso no permitido por robots.txt para {url}')
    else:
        print(f'Error al hacer la solicitud HTTP. Código de estado: {response.status_code}')
    
    # Imprimir el contenido HTML para depuración
    print("Contenido HTML de la página:")
    print(response.text[:500])  # Imprimir los primeros 500 caracteres del HTML

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
    
# URL de la página que quieres hacer scraping
url = 'https://www.diariooficial.interior.gob.cl/edicionelectronica/index.php?date=09-10-2024&edition=43969'

if is_allowed_by_robots(url):
    scrape_page(url)
else:
    print(f'Acceso no permitido por robots.txt para {url}')


    