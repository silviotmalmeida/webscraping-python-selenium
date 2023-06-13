# script com função de baixar mangás no site novelmania.com.br

# importando as dependências
from selenium import webdriver  # biblioteca de automação de testes
import time  # biblioteca para permitir sleep de execução
import requests  # biblioteca de requisições http
from bs4 import BeautifulSoup  # biblioteca de tratamento de html
import os  # biblioteca de manipulação de pastas

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
    next_url = 'https://novelmania.com.br/novels/cheat-do-crescimento/capitulos/volume-3-lista-de-personagens'

    # inicializando o condicional do laço de captura
    continue_script = True

    # iniciando o laço de captura
    while continue_script:

        print(f'{next_url}\n')

        # definindo o volume a ser baixado
        volume_number = next_url.split("volume-")[1].split("-")[0].zfill(3)
        # volume_number = '001'
        
        # definindo o capítulo a ser baixado
        if "prologo" in next_url:
            chapter_number = '000_prologo'
        elif "epilogo" in next_url:
            chapter_number = 'ZZZ_epilogo'
        elif "lista-de-personagens" in next_url:
            chapter_number = 'ZZZ_lista-de-personagens'
        else:
            chapter_number = next_url.split("capitulo-")[1].split("-")[0].zfill(3)
        # chapter_number = '208'
        
        # definindo as tags da página de saída
        initial_tags=f'<html><head><title>volume {volume_number} / capítulo {chapter_number}</title></head><body>'
        final_tags=f'</body></html>'

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
        time.sleep(5)

        # tratando o html recebido
        html = BeautifulSoup(driver.page_source, 'html.parser')

        # apagando tags desnecessárias
        for data in html(['img', 'hr']):
            data.decompose()

        # iterando sobre as tags <div> do html
        for div in html.select('div'):

            # se o atributo id da tag possuir os caracteres 'chapter-content', corresponde ao conteúdo do capítulo
            if div.get('id') != None and 'chapter-content' in div.get('id'):

                # criando e salvando a página em um arquivo
                output_file = open(f'{project_folder}/{files_folder}/{volume_number}-{chapter_number}.html','w')
                output_file.write(initial_tags)
                output_file.write(str(div))
                output_file.write(final_tags)

        # fechando o driver
        driver.quit()    

        # inicializando o link do próximo capítulo
        next_url = 'https://novelmania.com.br'

        # inicializando o condicional do laço de captura
        continue_script = True

        # iterando sobre as tags <a> do html
        for url in html.select('a'):

            # se o atributo title da tag possuir os caracteres 'Próximo capítulo', corresponde ao link do próximo capítulo
            if url.get('title') != None and 'Próximo capítulo' in url.get('title'):

                # obtendo o link do próximo capítulo
                next_url = 'https://novelmania.com.br' + url.get('href')

        # se não foi localizado o link do próximo capitulo, encerra o laço
        if next_url == 'https://novelmania.com.br':
            continue_script = False

        print(f'Arquivo {volume_number}-{chapter_number}.html pronto.\n')

        # descomente para executar uma vez
        # exit()

# em caso de erro:
except Exception as error:

    # exibe a mensagem
    print(f"Ocorreu um erro. {error}")

    # encerra a execução do script
    exit()
