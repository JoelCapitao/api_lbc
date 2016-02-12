#!/bin/bash

USERNAME=$1
PASSWORD=$2
PAGE_FILENAME=$3
COOKIE_JAR='./cookie_api_lbc.jar'

if [ ! -f ${COOKIE_JAR} ]; then
./cookie_gen.sh ${USERNAME} ${PASSWORD}
fi

curl -ksL -b ${COOKIE_JAR} "https://compteperso.leboncoin.fr/account/index.html?ca=12_s" > ${PAGE_FILENAME}
