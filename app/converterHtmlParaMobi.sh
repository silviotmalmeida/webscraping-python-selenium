#!/bin/bash
# precisa do calibre instalado (sudo apt install calibre)

for i in *.html;
  do name=`echo "$i" | cut -d'.' -f1`
  echo "$name"
  ebook-convert "${name}.html" "${name}.mobi"
done
