#!/bin/bash

USERNAME=$1
TMP_PAGE_FILE=$2
COOKIE_JAR_FILE=$3

if [ ! -f ${COOKIE_JAR_FILE} ]; then
./cookie_gen.sh ${USERNAME} ${COOKIE_JAR_FILE}
fi

curl -ksL -b ${COOKIE_JAR_FILE} "https://compteperso.leboncoin.fr/account/index.html?ca=12_s" > ${TMP_PAGE_FILE}
