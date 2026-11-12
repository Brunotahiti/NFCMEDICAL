#!/bin/sh
# Prépare le site à publier sur https://manaprocess.cloud/materiel/ dans deploy/site/materiel.
set -e
cd "$(dirname "$0")/.."
OUT=deploy/site/materiel
rm -rf deploy/site
mkdir -p "$OUT/photos"
{
  printf '%s\n' '<!doctype html>' '<html lang="fr">' '<head>' '<meta charset="utf-8">' \
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">' \
    '<base href="/materiel/">' \
    '<style>:root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px);-webkit-text-size-adjust:100%}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>' \
    '</head>' '<body>'
  cat index.html
  printf '%s\n' '</body>' '</html>'
} > "$OUT/index.html"
cp photos/*.jpg "$OUT/photos/"
echo "Site prêt dans $OUT"
