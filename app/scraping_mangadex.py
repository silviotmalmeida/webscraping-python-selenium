# script com função de baixar mangás no site novelmania.com.br

# importando as dependências
from selenium import webdriver  # biblioteca de automação de testes
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
import time # biblioteca para permitir sleep de execução
import requests  # biblioteca de requisições http
from bs4 import BeautifulSoup  # biblioteca de tratamento de html
import subprocess  # biblioteca de comandos do sistema
import os  # biblioteca de manipulação de pastas
import shutil  # biblioteca de manipulação de pastas
import re  # biblioteca de expressões regulares
from PIL import Image # biblioteca para tratamento de imagens
import pillow_avif # plugin adicional para o pillow

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
    next_url = 'https://mangadex.org/chapter/bb7a70c0-4c91-4adc-b1f9-d23b7b2dceb7'
    
    # inicializando o condicional do laço de captura
    continue_script = True

    # iniciando o laço de captura
    while continue_script:

        print(f'{next_url}\n')
                
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

        # inicializando variável de espera de carregamento da página
        page_loading = True
        while page_loading:
            time.sleep(10)
            # tratando o html recebido
            html = BeautifulSoup(driver.page_source, 'html.parser')

            # inicializando o número do capítulo
            chapter_number = '-1'

            # coletando todas as tag <div> da url do capítulo
            for div in html.select('div'):

                # se o atributo class da div possuir os caracteres 'chapter', prossegue:
                if div.get('class') != None and 'chapter' in div.get('class'):

                    # se o texto possuir os caracteres 'Ch.', corresponde ao número do capítulo
                    if div.text != None and 'Ch. ' in div.text:

                        chapter_number = div.text.split("Ch. ")[1].zfill(6).replace('.','-')
         
            # se o número do capítulo  ão for descoberto, lança uma exceção
            if chapter_number == '-1':
                raise Exception(
                    f'Não foi possível identificar o número do capítulo!')
            
            # inicializando a url do próximo capítulo
            next_url = 'empty'

            # coletando todas as tag <a> da url do capítulo
            for a in html.select('a'):

                # se o atributo href da a possuir os caracteres '/chapter/', prossegue:
                if a.get('href') != None and '/chapter/' in a.get('href'):

                    next_url = 'https://mangadex.org' + a.get('href')
         
            # se o número do capítulo  não for descoberto, lança uma exceção
            if next_url == 'empty':
                raise Exception(
                    f'Não foi possível identificar a url do próximo capítulo!')
            
            # coletando todas as tag <img> da url do capítulo
            images = html.select('img')
            # se forem encontradas poucas imagens, recarrega a página
            if len(images) < 3:
                print(f'Recarregando a página...\n')
                driver.refresh()
            else:
                # considerando a página carregada
                page_loading = False
        
                # se a pasta do capítulo ainda não existir, será criada
                if not os.path.isdir(f'{project_folder}/{files_folder}/{chapter_number}'):
                    os.mkdir(f'{project_folder}/{files_folder}/{chapter_number}')

                # coletando todas as tag <img> da url do capítulo
                for image in html.select('img'):

                    # se o atributo alt da tag possuir os caracteres '-' e '.', corresponde ao conteúdo do capítulo
                    if image.get('alt') != None and '-' in image.get('alt') and '.' in image.get('alt'):

                        # obtendo a url da imagem a partir do atributo src
                        image_url = image.get('src')

                        # obtendo a extensão do arquivo
                        # image_extension = image.get('alt').split('.')[-1]
                        image_extension = 'png'

                        # definindo a página da imagem a partir do atributo alt, e configurando com 4 dígitos
                        image_page = image.get('alt').split('-')[0].strip().zfill(4)

                        # abrindo a nova aba com a imagem
                        # driver.get(image_url)
                        # driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + 't')
                        main_window= driver.current_window_handle
                        driver.execute_script("window.open(''),'_blank'")
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(image_url)

                        # aguardando a aba carregar
                        time.sleep(5)

                        # ajustando o tamanho da janela à imagem
                        driver.maximize_window()
                        width = driver.execute_script("return Math.max( document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );")
                        height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
                        driver.set_window_size(width, height)

                        time.sleep(5)

                        # capturando a tela
                        full_page = driver.find_element(By.TAG_NAME, "body")
                        full_page.screenshot(f"{project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}")

                        driver.close()
                        driver.switch_to.window(main_window)

                        # # abrindo a imagem original
                        # old_image = Image.open(
                        #     f'{project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}').convert('RGB')

                        # # obtendo as dimensões da imagem original
                        # width, height = old_image.size

                        # # definindo o width máximo da imagem
                        # new_width = 960

                        # # se a imagem original for maior:
                        # if width > new_width:

                        #     # calcula o novo height para manter a proporção
                        #     new_height = round((new_width*height)/width)

                        #     # cria uma nova imagem redimensionada
                        #     new_image = old_image.resize(
                        #         (new_width, new_height), Image.LANCZOS)

                        # # senão
                        # else:

                        #     # mantém as dimensões originais
                        #     new_image = old_image

                        # # salvando a nova imagem, otimizando a qualidade
                        # new_image.save(
                        #     f'{project_folder}/{files_folder}/{chapter_number}/_{image_page}.jpg',
                        #     optimize=True,
                        #     quality=50,
                        # )

                        # # apagando a imagem original
                        # cmd = subprocess.run(
                        #     f"rm -rf '{project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}'", shell=True)

                        # # se ocorrer um erro, lança uma exceção
                        # if cmd.returncode != 0:
                        #     raise Exception(
                        #         f'Erro apagando a imagem {project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}')

        # fechando o driver
        driver.quit()

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
        
        print(f'Arquivo {chapter_number}.pdf pronto.\n')

        # descomente para executar uma vez
        # exit()

# em caso de erro:
except Exception as error:

    # exibe a mensagem
    print(f"Ocorreu um erro. {error}")

    # encerra a execução do script
    exit()
