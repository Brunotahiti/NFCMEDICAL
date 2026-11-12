# Image du site MédiParc servi sur https://manaprocess.cloud/materiel/
# Contexte de construction : la racine du dépôt. Le site est généré pendant la construction.
FROM alpine:3.20 AS build
WORKDIR /src
COPY index.html ./
COPY photos ./photos
COPY deploy/build.sh ./deploy/build.sh
RUN sh deploy/build.sh

FROM nginx:1.27-alpine
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/deploy/site/ /usr/share/nginx/html/
