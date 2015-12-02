#!/bin/bash

USERNAME=$1
PASSWORD=$2
COOKIE_JAR='./cookie_api_lbc.jar'

function cookie_gen() {
# Génération du cookie
HEADERS_1=$(echo -H 'Content-Type:application/x-www-form-urlencoded')
curl -s -b ${COOKIE_JAR} -c ${COOKIE_JAR} -X POST --data "st_username=${USERNAME}&st_passwd=${PASSWORD}" ${HEADERS_1} -k "https://compteperso.leboncoin.fr/store/verify_login/0"
}

cookie_gen

# Première requête
HEADERS_2=$(echo -H 'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'  -H 'Accept-Language:fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.' -H 'Cookie:cookieFrame=2;s=red1xb6d79b789f7b65c88305075b9e8ff3972f32ee98;xtvrn=$266818$' -H 'DNT:1' -H 'Host:compteperso.leboncoin.fr' -H 'Referer:http://www.leboncoin.fr/annonces/offres/ile_de_france/' -H 'Upgrade-Insecure-Requests:1' -H 'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')
curl -k -s -L ${HEADERS_2} https://compteperso.leboncoin.fr/account/index.html?ca=12_s >/dev/null 2>&1

cookie_gen
