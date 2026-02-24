# script com função de baixar mangás no site weebcentral.com

# importando as dependências
from selenium import webdriver  # biblioteca de automação de testes
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
import time  # biblioteca para permitir sleep de execução
import requests  # biblioteca de requisições http
from bs4 import BeautifulSoup  # biblioteca de tratamento de html
import subprocess  # biblioteca de comandos do sistema
import os  # biblioteca de manipulação de pastas
import shutil  # biblioteca de manipulação de pastas
import re  # biblioteca de expressões regulares
from PIL import Image  # biblioteca para tratamento de imagens
import pillow_avif  # plugin adicional para o pillow

# função auxiliar para converter o número do capítulo em um valor numérico, para facilitar a ordenação dos arquivos
def chapter_value(chapter):
    # inicializando as variáveis de valor e potência
    value = 0
    potencia = 0
    # convertendo o número do capítulo em uma lista de caracteres
    chars = list(chapter)
    # percorrendo a lista de caracteres do número do capítulo de trás para frente
    for char in reversed(chars):
        # se o caractere for um dígito, converte para inteiro e soma ao valor, multiplicando pela potência de 10 correspondente
        if char.isdigit():
            value = value + int(char) * (10**potencia)

        # incrementando a potência para o próximo dígito
        potencia = potencia + 1

    return value

# função auxiliar para iniciar o driver
def start_driver():
    options = webdriver.ChromeOptions()

    # Headless moderno (mais difícil de detectar)
    options.add_argument("--headless")

    # Tamanho realista
    options.add_argument("--window-size=1920,1080")

    # Remove sinais óbvios
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # User agent realista
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)

    # Aplicar stealth
    stealth(driver,
            languages=["pt-BR", "pt"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
    )

    # Remove navigator.webdriver manualmente
    driver.execute_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    })
    """)

    return driver
#
#
# Início do script
#
#
# obtendo a pasta do projeto
project_folder = os.path.dirname(os.path.realpath(__file__))

# nomeando a pasta de saída dos arquivos
files_folder = "files"

# tratamento de exceções 
try:

    # se a pasta de arquivos ainda não existir, será criada
    if not os.path.isdir(f"{project_folder}/{files_folder}"):
        os.mkdir(f"{project_folder}/{files_folder}")

    # inicializando o link do capítulo inicial
    initial_url = "https://weebcentral.com/chapters/01J76XZ34MHTRP2G4YRW2478WA"

    # definindo as opções do driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    print(
        f"Tentando obter a URL da página de capítulos a partir da URL: {initial_url}\n"
    )

    # fazendo a requisição na url principal para obter os links dos capítulos
    driver = start_driver()
    driver.get(initial_url) 

    # inicializando variável de espera de carregamento da página
    page_loading = True
    while page_loading:
        time.sleep(10)
        # tratando o html recebido
        html = BeautifulSoup(driver.page_source, "html.parser")

        # fechando o driver
        driver.quit()

        # inicializando o número do capítulo
        initial_chapter_number = "-1"

        # coletando todas as tag <span> da url do capítulo
        for span in html.select("span"):

            # se o texto da span possuir os caracteres ' - Chapter ', prossegue:
            if span.text != None and " - Chapter " in span.text:

                # obtendo a url da página de seleção de capítulos
                urls_page = span.find_parent("button").get("hx-get")
                # obtendo o número da temporada
                season_number = (
                    span.text.split(" - Chapter ")[0].strip().replace("S", "").zfill(2)
                )
                # obtendo o número do capítulo e formatando com 6 dígitos, e substituindo pontos por hífens
                initial_chapter_number = f"{season_number}{span.text.split(' - Chapter ')[1].strip().zfill(6).replace('.','-')}"

        # se o número do capítulo não for descoberto, lança uma exceção
        if initial_chapter_number == "-1":
            raise Exception(
                f"Não foi possível identificar o número do capítulo inicial!"
            )

        # fazendo a requisição na urls_page para obter os links dos capítulos
        driver = start_driver()
        driver.get(urls_page)
        time.sleep(10)
        # tratando o html recebido
        html = BeautifulSoup(driver.page_source, "html.parser")

        # coletando todas as tag <a> da url do capítulo
        a = html.select("a")
        # se forem encontradas poucas urls, recarrega a página
        if len(a) < 30:
            print(f"Recarregando a página...\n")
            driver.refresh()
        # senão, considera a página carregada
        else:
            page_loading = False

            # fechando o driver
            driver.quit()

            # inicializando a lista de capítulos
            chapters = []

            # inserindo o capítulo atual na lista de capítulos
            chapters.append(
                f"{chapter_value(initial_chapter_number)} {initial_chapter_number} {initial_url}"
            )

            # coletando todas as tag <a> da url do capítulo
            for a in html.select("a"):

                # se o texto da a possuir os caracteres ' - Chapter ', prossegue:
                if a.text != None and " - Chapter " in a.text:

                    # inicializando o número do capítulo
                    chapter_number = "-1"

                    # obtendo o número da temporada
                    season_number = (
                        a.text.split(" - Chapter ")[0].strip().replace("S", "").zfill(2)
                    )
                    # obtendo o número do capítulo e formatando com 6 dígitos, e substituindo pontos por hífens
                    chapter_number = f"{season_number}{a.text.split(' - Chapter ')[1].strip().zfill(6).replace('.','-')}"

                    # se o número do capítulo não for descoberto, lança uma exceção
                    if chapter_number == "-1":
                        raise Exception(
                            f"Não foi possível identificar o número do capítulo!"
                        )

                    # inserindo o capítulo atual na lista de capítulos
                    chapters.append(
                        f"{chapter_value(chapter_number)} {chapter_number} {a.get('href')}"
                    )

    print(f"Foi obtida uma lista com {len(chapters)} capítulos!\n")

    # ordenando a lista de capítulos pelo valor numérico do capítulo
    chapters.sort()

    # iterando sobre a lista de capítulos para baixar os arquivos
    for chapter in chapters:

        # obtendo os dados do item atual
        value = chapter.split(" ")[0]
        chapter_number = chapter.split(" ")[1]
        chapter_url = chapter.split(" ")[2]

        if int(value) >= int(chapter_value(initial_chapter_number)):

            print(f"Capturando capítulo {chapter}...\n")

            # fazendo a requisição na urls_page para obter os links das imagens do capitulo
            driver = start_driver()
            driver.get(chapter_url)

            # inicializando variável de espera de carregamento da página
            page_loading = True
            while page_loading:
                time.sleep(10)
                # tratando o html recebido
                html = BeautifulSoup(driver.page_source, "html.parser")

                # coletando todas as tag <img> da url do capítulo
                images = html.select("img")
                # se forem encontradas poucas imagens, recarrega a página
                if len(images) < 3:
                    print(f"Recarregando a página...\n")
                    driver.refresh()
                else:
                    # considerando a página carregada
                    page_loading = False

                    # fechando o driver
                    driver.quit()

                    # se a pasta do capítulo ainda não existir, será criada
                    if not os.path.isdir(
                        f"{project_folder}/{files_folder}/{chapter_number}"
                    ):
                        os.mkdir(f"{project_folder}/{files_folder}/{chapter_number}")

                    # coletando todas as tag <img> da url do capítulo
                    for image in html.select("img"):

                        # se o atributo alt da tag possuir os caracteres 'Page', corresponde ao conteúdo do capítulo
                        if image.get("alt") != None and "Page" in image.get("alt"):
                            # obtendo a url da imagem a partir do atributo src
                            image_url = image.get("src")

                            # obtendo a extensão do arquivo
                            image_extension = image.get("src").split(".")[-1]
                            # image_extension = "png"

                            # definindo a página da imagem a partir do atributo alt, e configurando com 4 dígitos
                            image_page = image.get("alt").split(" ")[1].strip().zfill(4)

                            # abrindo a imagem
                            driver = start_driver()
                            driver.get(image_url)

                            # aguardando a aba carregar
                            time.sleep(5)

                            # ajustando o tamanho da janela à imagem
                            driver.maximize_window()
                            width = driver.execute_script(
                                "return Math.max( document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth );"
                            )
                            height = driver.execute_script(
                                "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );"
                            )
                            driver.set_window_size(width, height)

                            # aguardando a aba carregar
                            time.sleep(5)

                            # capturando a tela
                            full_page = driver.find_element(By.TAG_NAME, "body")
                            full_page.screenshot(
                                f"{project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}"
                            )

                            # fechando o driver
                            driver.quit()

                            # abrindo a imagem original
                            old_image = Image.open(
                                f"{project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}"
                            ).convert("RGB")

                            # obtendo as dimensões da imagem original
                            width, height = old_image.size

                            # definindo o width máximo da imagem
                            new_width = 960

                            # se a imagem original for maior:
                            if width > new_width:

                                # calcula o novo height para manter a proporção
                                new_height = round((new_width * height) / width)

                                # cria uma nova imagem redimensionada
                                new_image = old_image.resize(
                                    (new_width, new_height), Image.LANCZOS
                                )

                            # senão
                            else:

                                # mantém as dimensões originais
                                new_image = old_image

                            # salvando a nova imagem, otimizando a qualidade
                            new_image.save(
                                f"{project_folder}/{files_folder}/{chapter_number}/_{image_page}.jpg",
                                optimize=True,
                                quality=100,
                            )

                            # apagando a imagem original
                            cmd = subprocess.run(
                                f"rm -rf '{project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}'",
                                shell=True,
                            )

                            # se ocorrer um erro, lança uma exceção
                            if cmd.returncode != 0:
                                raise Exception(
                                    f"Erro apagando a imagem {project_folder}/{files_folder}/{chapter_number}/{image_page}.{image_extension}"
                                )

                    # utilizando o imagemagick para realizar converter o capítulo em pdf
                    cmd = subprocess.run(
                        f"cd '{project_folder}/{files_folder}/{chapter_number}/'; convert * '{chapter_number}.pdf'",
                        shell=True,
                    )

                    # se ocorrer um erro, lança uma exceção
                    if cmd.returncode != 0:
                        raise Exception(f"Erro convertendo o capítulo {chapter_number}")

                    # movendo o capítulo em pdf para a pasta de arquivos
                    cmd = subprocess.run(
                        f"mv '{project_folder}/{files_folder}/{chapter_number}/{chapter_number}.pdf' '{project_folder}/{files_folder}/{chapter_number}.pdf'",
                        shell=True,
                    )

                    # se ocorrer um erro, lança uma exceção
                    if cmd.returncode != 0:
                        raise Exception(f"Erro movendo o capítulo {chapter_number}")

                    # apagando a pasta com as imagens
                    cmd = subprocess.run(
                        f"rm -rf '{project_folder}/{files_folder}/{chapter_number}/'",
                        shell=True,
                    )

                    # se ocorrer um erro, lança uma exceção
                    if cmd.returncode != 0:
                        raise Exception(
                            f"Erro apagando a pasta {project_folder}/{files_folder}/{chapter_number}"
                        )

                    print(f"Arquivo {chapter_number}.pdf pronto.\n")

                    # descomente para executar uma vez
                    # exit()

# em caso de erro:
except Exception as error:

    # exibe a mensagem
    print(f"Ocorreu um erro. {error}")

    # encerra a execução do script
    exit()
