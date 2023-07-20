#!/bin/bash
# precisa do calibre instalado (sudo apt install calibre)

for i in *.pdf;
  do name=`echo "$i" | cut -d'.' -f1`
  echo "$name"
  ebook-convert "${name}.pdf" "${name}.epub"
done
