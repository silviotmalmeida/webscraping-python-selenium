#!/bin/bash

echo ""
docker container exec -it webscraping-python-selenium python3 /root/scraping_unionleitor.py

sleep 1

echo "Definindo permissoes da pasta de código-fonte..."
docker container exec webscraping-python-selenium sudo chmod 777 -R /root
sleep 1

echo "Processo concluído."
