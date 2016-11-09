#!/usr/bin/python2.7
#-*- coding: utf-8 -*-
""" Ce script permet de recuperer les informations
du site lbc """

# from pdb import set_trace as st
from collections import OrderedDict
from datetime import datetime
from time import time
from subprocess import Popen, PIPE
from sys import argv
from os import remove, path
import bs4 as BeautifulSoup

try:
    USERNAME = argv[1]
    CSV_FILE_OUTPUT = argv[2]
except IndexError:
    print '%s USERNAME CSV_FILE_OUTPUT [FORCE_HEADER=True]' % argv[0]
    exit(1)


TMP_PAGE_FILE = './tmp_page.html'
COOKIE_JAR_FILE = '/tmp/cookie_api_lbc.jar'

TIME_NOW = time()
TIMESTAMP = datetime.fromtimestamp(TIME_NOW).strftime('%Y%m%d%H%M%S')

if not path.isfile(COOKIE_JAR_FILE):
    print 'Veuillez entrer votre mot de passe : '

POPEN = Popen(('./utils/page_gen.sh', USERNAME, TMP_PAGE_FILE, COOKIE_JAR_FILE), stdout=PIPE)
POPEN.wait()

TMP_PAGE = open(TMP_PAGE_FILE, 'r')
SOUP = BeautifulSoup.BeautifulSoup(TMP_PAGE.read(), 'lxml')
TMP_PAGE.close()

OBJECTS = {}
for i, title in enumerate(SOUP.find_all('div', 'title')):
    o = {}
    o['title'] = str(title.a.contents[0].encode('utf-8').decode('ascii', 'ignore'))
    o['price'] = -1
    o['vues'] = -1
    o['mails'] = -1
    o['clics'] = -1
    OBJECTS[i] = o

for i, price in enumerate(SOUP.find_all('div', 'price')):
    OBJECTS[i]['price'] = int(price.contents[0].encode('utf-8').replace(' \xe2\x82\xac', ''))

for i, o in enumerate(OBJECTS):
    OBJECTS[i]['vues'] = int(SOUP('span', 'square')[i*3].contents[0])
    OBJECTS[i]['mails'] = int(SOUP('span', 'square')[i*3+1].contents[0])
    OBJECTS[i]['clics'] = int(SOUP('span', 'square')[i*3+2].contents[0])

# Changement de l'ordre
OBJECTS_R = OrderedDict(sorted(OBJECTS.items(), reverse=True))

# VUES
if not path.isfile(CSV_FILE_OUTPUT):
    CSV_FILE_OUTPUT_FILE = open(CSV_FILE_OUTPUT, 'w')
    CSV_FILE_OUTPUT_FILE.write('timestamp;')
    for o in OBJECTS_R:
        CSV_FILE_OUTPUT_FILE.write('%s ( %s € );' % (OBJECTS_R[o]['title'], OBJECTS_R[o]['price']))
    CSV_FILE_OUTPUT_FILE.write('\n')
else:
    CSV_FILE_OUTPUT_FILE = open(CSV_FILE_OUTPUT, 'a')


CSV_FILE_OUTPUT_FILE.write('%s;' % TIMESTAMP)
for o in OBJECTS_R:
    CSV_FILE_OUTPUT_FILE.write('%s;' % OBJECTS_R[o]['vues'])
CSV_FILE_OUTPUT_FILE.write('\n')


# print()



# # CLICS
# print(TIMESTAMP, end=';')
# for i, o in enumerate(OBJECTS):
#     print('%s' % OBJECTS[i]['clics'], end=';')

# print()

# # MAILS
# print(TIMESTAMP, end=';')
# for i, o in enumerate(OBJECTS):
#     print('%s' % OBJECTS[i]['mails'], end=';')

# print()

# Nettoyage
remove(TMP_PAGE_FILE)
