#!/usr/bin/python2.7
#-*- coding: utf-8 -*-
""" Ce script permet de recuperer les informations
du site lbc """

from pdb import set_trace as st
from collections import OrderedDict
from datetime import datetime
from time import time
from subprocess import Popen, PIPE
from sys import argv
from os import remove, path
import bs4 as BeautifulSoup

try:
    USERNAME = argv[1]
    CSV_PATH = argv[2]
except IndexError:
    print '%s USERNAME CSV_PATH' % argv[0]
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

# Generation of the list
OBJECTS = {}
for i, title in enumerate(SOUP.find_all('div', 'title')):
    o = {}
    st()
    o['url'] = title.a.attrs['href']
    o['title'] = title.a.string
    # o['title'] = str(title.a.contents[0].encode('utf-8').decode('ascii', 'ignore'))
    o['price'] = -1
    o['views'] = -1
    o['mails'] = -1
    o['clics'] = -1
    OBJECTS[i] = o

for i, price in enumerate(SOUP.find_all('div', 'price')):
    OBJECTS[i]['price'] = int(price.contents[0].encode('utf-8').replace(' \xe2\x82\xac', ''))

for i, o in enumerate(OBJECTS):
    OBJECTS[i]['views'] = int(SOUP('span', 'square')[i*3].contents[0])
    OBJECTS[i]['mails'] = int(SOUP('span', 'square')[i*3+1].contents[0])
    OBJECTS[i]['clics'] = int(SOUP('span', 'square')[i*3+2].contents[0])

# Changement de l'ordre
OBJECTS_R = OrderedDict(sorted(OBJECTS.items(), reverse=True))

for o in OBJECTS_R:
    CSV_OUTPUT = '%s/%s.csv' % (CSV_PATH, OBJECTS_R[o]['title'])
    if not path.isfile(CSV_OUTPUT):
        CSV_OUTPUT_FILE = open(CSV_OUTPUT, 'w')
        CSV_OUTPUT_FILE.write('timestamp;price;views;clics;mails;\n')
    else:
        CSV_OUTPUT_FILE = open(CSV_OUTPUT, 'a')
    CSV_OUTPUT_FILE.write('%s;%s;%s;%s;%s;\n' % (TIMESTAMP, OBJECTS_R[o]['price'], OBJECTS_R[o]['views'], OBJECTS_R[o]['clics'], OBJECTS_R[o]['mails']))

CSV_OUTPUT_FILE.close()

# Cleaning
remove(TMP_PAGE_FILE)
