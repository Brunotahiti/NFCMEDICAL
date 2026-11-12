# Image du site MédiParc servi sur https://manaprocess.cloud/materiel/
# Contexte de construction : la racine du dépôt, après deploy/build.sh.
FROM nginx:1.27-alpine
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY deploy/site/ /usr/share/nginx/html/
