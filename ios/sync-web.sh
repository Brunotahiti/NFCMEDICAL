#!/bin/sh
# Copie la démo web (index.html + photos) dans le projet Xcode, en ajoutant l'en-tête HTML complet.
set -e
cd "$(dirname "$0")/.."
OUT=ios/MediParcNFC/Web
rm -rf "$OUT/photos"
mkdir -p "$OUT/photos"
{
  printf '%s\n' '<!doctype html>' '<html lang="fr">' '<head>' '<meta charset="utf-8">' \
    '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">' \
    '<style>:root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px);-webkit-text-size-adjust:100%}body{margin:0;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}input{-webkit-user-select:text;user-select:text}img{max-width:100%}[hidden]{display:none!important}</style>' \
    '</head>' '<body>'
  cat index.html
  printf '%s\n' '</body>' '</html>'
} > "$OUT/index.html"
cp photos/*.jpg "$OUT/photos/"
echo "Web synchronisé dans $OUT"
