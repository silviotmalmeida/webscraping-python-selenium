# script com função de baixar mangás no site novelmania.com.br

# importando as dependências
from selenium import webdriver  # biblioteca de automação de testes
import time # biblioteca para permitir sleep de execução
import requests  # biblioteca de requisições http
from bs4 import BeautifulSoup  # biblioteca de tratamento de html
import subprocess  # biblioteca de comandos do sistema
import os  # biblioteca de manipulação de pastas
import shutil  # biblioteca de manipulação de pastas
import re  # biblioteca de expressões regulares
from PIL import Image # biblioteca para tratamento de imagens

# obtendo a pasta do projeto
project_folder = os.path.dirname(os.path.realpath(__file__))

# nomeando a pasta de saída dos arquivos
files_folder = 'files'

# tratamento de exceções
try:

    # se a pasta de arquivos ainda não existir, será criada
    if not os.path.isdir(f'{project_folder}/{files_folder}'):
        os.mkdir(f'{project_folder}/{files_folder}')

    # inicializando o link do próximo capítulo
    # next_url = 'https://slimeread.com/ler/2618/cap-15'
    next_url = 'https://slimeread.com/ler/6901/cap-6'

    manga_id = next_url.split("/")[4]

    # inicializando o condicional do laço de captura
    continue_script = True

    # iniciando o laço de captura
    while continue_script:

        print(f'{next_url}\n')

        # definindo o capítulo a ser baixado
        chapter_number = next_url.split("cap-")[1].zfill(4)
        # chapter_number = '0001'
                
        # fazendo a requisição na url principal para saber se o site esta no ar
        response = requests.get(next_url)

        # fechando a conexão
        response.close()

        # se a requisição não retornar dados, lança uma exceção
        if not 200 == response.status_code:
            raise Exception(f'Falha na requisição, código {response.status_code}')

        # fazendo a requisição na url principal com o selenium para obter os links
        driver = webdriver.Remote(
            command_executor='http://0.0.0.0:4444/wd/hub',
            options=webdriver.ChromeOptions()
        )
        driver.get(next_url)
        time.sleep(25)

        # tratando o html recebido
        html = BeautifulSoup(driver.page_source, 'html.parser')

        # fechando o driver
        driver.quit()

        # iniciando o dicionário que armazenará os pares { pasta : url interna }
        folder_url = {}

        # coletando todas as tag <img> da url do capítulo
        images = html.select('img')

        # se forem encontradas poucas imagens, lança uma exceção
        if len(images) < 3:
            raise Exception(
                f'Quantidade de imagens({len(images)}) menor que 6')
        
        # se a pasta do capítulo ainda não existir, será criada
        if not os.path.isdir(f'{project_folder}/{files_folder}/{chapter_number}'):
            os.mkdir(f'{project_folder}/{files_folder}/{chapter_number}')

        # coletando todas as tag <img> da url do capítulo
        for image in html.select('img'):

            # se o atributo alt da tag possuir os caracteres 'agina ', corresponde ao conteúdo do capítulo
            if image.get('alt') != None and 'agina ' in image.get('alt'):

                # obtendo a url da imagem a partir do atributo src
                image_url = image.get('src')

                # obtendo a extensão do arquivo
                image_extension = image_url.split('.')[-1]

                # definindo a página da imagem a partir do atributo pag, e configurando com 4 dígitos
                image_page = image.get('alt').split('agina ')[1].strip().zfill(4)

                # utilizando o wget para realizar o download da imagem
                cmd = subprocess.run(
                    f"wget --tries=99 -O '{project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}' '{image_url}'", shell=True)
                
                # se ocorrer um erro, lança uma exceção
                if cmd.returncode != 0:
                    raise Exception(f'Erro baixando a imagem {image_url} para a pasta {project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}')

                # abrindo a imagem original
                old_image = Image.open(
                    f'{project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}').convert('RGB')

                # obtendo as dimensões da imagem original
                width, height = old_image.size

                # definindo o width máximo da imagem
                new_width = 960

                # se a imagem original for maior:
                if width > new_width:

                    # calcula o novo height para manter a proporção
                    new_height = round((new_width*height)/width)

                    # cria uma nova imagem redimensionada
                    new_image = old_image.resize(
                        (new_width, new_height), Image.LANCZOS)

                # senão
                else:

                    # mantém as dimensões originais
                    new_image = old_image

                # salvando a nova imagem, otimizando a qualidade
                new_image.save(
                    f'{project_folder}/{files_folder}/{chapter_number}/_{image_page}.{image_extension}',
                    optimize=True,
                    quality=50
                )

                # apagando a imagem original
                cmd = subprocess.run(
                    f"rm -rf '{project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}'", shell=True)

                # se ocorrer um erro, lança uma exceção
                if cmd.returncode != 0:
                    raise Exception(
                        f'Erro apagando a imagem {project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}')

        # utilizando o imagemagick para realizar converter o capítulo em pdf            
        cmd = subprocess.run(
            f"cd '{project_folder}/{files_folder}/{chapter_number}/'; convert * '{chapter_number}.pdf'", shell=True)

        # se ocorrer um erro, lança uma exceção
        if cmd.returncode != 0:
            raise Exception(
                f'Erro convertendo o capítulo {chapter_number}')

        # movendo o capítulo em pdf para a pasta de arquivos            
        cmd = subprocess.run(
            f"mv '{project_folder}/{files_folder}/{chapter_number}/{chapter_number}.pdf' '{project_folder}/{files_folder}/{chapter_number}.pdf'", shell=True)

        # se ocorrer um erro, lança uma exceção
        if cmd.returncode != 0:
            raise Exception(f'Erro movendo o capítulo {chapter_number}')

        # apagando a pasta com as imagens            
        cmd = subprocess.run(
            f"rm -rf '{project_folder}/{files_folder}/{chapter_number}/'", shell=True)

        # se ocorrer um erro, lança uma exceção
        if cmd.returncode != 0:
            raise Exception(
                f'Erro apagando a pasta {project_folder}/{files_folder}/{chapter_number}')

        # inicializando o link do próximo capítulo
        next_url = 'https://slimeread.com'

        # inicializando o condicional do laço de captura
        continue_script = True

        # iterando sobre as tags <a> do html
        for url in html.select('a'):

            # se o atributo href da tag possuir os caracteres 'cap-' e o id do manga, corresponde ao link do próximo capítulo
            if url.get('href') != None and 'cap-' in url.get('href') and manga_id in url.get('href'):

                url_chapter = ('https://slimeread.com' + url.get('href')).split("cap-")[1].zfill(4)

                if float(url_chapter) > float(chapter_number):

                    # obtendo o link do próximo capítulo
                    next_url = 'https://slimeread.com' + url.get('href')
                    break

        # se não foi localizado o link do próximo capitulo, encerra o laço
        if next_url == 'https://slimeread.com':
            continue_script = False
        
        print(f'Arquivo {chapter_number}.pdf pronto.\n')

        # descomente para executar uma vez
        # exit()

# em caso de erro:
except Exception as error:

    # exibe a mensagem
    print(f"Ocorreu um erro. {error}")

    # encerra a execução do script
    exit()
