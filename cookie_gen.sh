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
curl -k -s -L -b ${COOKIE_JAR} https://compteperso.leboncoin.fr/account/index.html?ca=12_s >/dev/null 2>&1

cookie_gen
