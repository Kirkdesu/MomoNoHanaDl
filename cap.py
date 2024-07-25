import os
import re
import zipfile
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Função para extrair o título e o capítulo do link
def extract_title_and_chapter(url):
    path = urlparse(url).path
    match = re.match(r'/manga/([^/]+)/capitulo-(\d+)', path)
    if match:
        title = match.group(1)
        chapter = match.group(2)
        return title, chapter
    return None, None

# Função para adicionar o sufixo se não estiver presente
def add_suffix_if_needed(url):
    if not url.endswith('/?style=list'):
        url = f"{url}/?style=list"
    return url

# Função para baixar as imagens
def download_image(url, folder_path, image_number):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        ext = url.split('.')[-1]
        image_path = os.path.join(folder_path, f"{image_number:02d}.{ext}")
        with open(image_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Imagem {image_number} baixada com sucesso.")
    else:
        print(f"Erro ao baixar a imagem {image_number}.")

# Função para criar um arquivo ZIP
def create_zip(folder_path, zip_name):
    zip_path = os.path.join(base_dir, f"{zip_name}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))
    print(f"Arquivo ZIP criado: {zip_path}")

# Função para excluir a pasta
def delete_folder(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(folder_path)
    print(f"Pasta {folder_path} excluída.")

# Links dos capítulos separados por vírgulas
links = [
    "https://momonohanascan.com/manga/amnesia-brilhante-e-alegre/capitulo-32",
    # Adicione mais links aqui
]

# Variáveis para controle de ZIP e exclusão de pasta
create_zip_file = True  # Define se deve criar o arquivo ZIP
delete_folder_after_zip = False  # Define se deve excluir a pasta após criar o ZIP

# Base da pasta de trabalho
base_dir = "momonohana"

for link in links:
    # Extrair o título e o capítulo
    titulo, capitulo = extract_title_and_chapter(link)

    if not titulo or not capitulo:
        print(f"Não foi possível extrair o título e o capítulo do link: {link}")
        continue

    # Adicionar o sufixo se necessário
    base_url = add_suffix_if_needed(link)

    # Criar a estrutura de diretórios
    obra_dir = os.path.join(base_dir, titulo)
    capitulo_dir = os.path.join(obra_dir, capitulo)
    os.makedirs(capitulo_dir, exist_ok=True)

    # Acessar a página e extrair as URLs das imagens
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    images = soup.select('img.wp-manga-chapter-img')

    # Baixar cada imagem
    for idx, img in enumerate(images):
        img_url = img['data-src'].strip()
        download_image(img_url, capitulo_dir, idx)

    # Criar o arquivo ZIP se a variável create_zip_file estiver True
    if create_zip_file:
        zip_name = capitulo
        create_zip(capitulo_dir, zip_name)

    # Excluir a pasta do capítulo se a variável delete_folder_after_zip estiver True
    if delete_folder_after_zip:
        delete_folder(capitulo_dir)

print("Processo concluído.")
