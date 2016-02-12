#!/usr/bin/python2.7
#-*- coding: utf-8 -*-
""" Ce script permet de recuperer les informations
du site lbc """

# from pdb import set_trace as st
from datetime import datetime
from time import time
from subprocess import Popen, PIPE
from sys import argv
from os import remove
import bs4 as BeautifulSoup

USERNAME = argv[1]
PASSWORD = argv[2]
if argv[3] is None:
    FORCE_HEADER = 'True'
else:
    FORCE_HEADER = argv[3]

TMP_PAGE_FILE = './tmp_page.html'

TIME_NOW = time()
TIMESTAMP = datetime.fromtimestamp(TIME_NOW).strftime('%Y%m%d%H%M%S')

POPEN = Popen(('./page_gen.sh', USERNAME, PASSWORD, TMP_PAGE_FILE), stdout=PIPE)
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

for i, obj in enumerate(OBJECTS):
    OBJECTS[i]['vues'] = int(SOUP('span', 'square')[i*3].contents[0])
    OBJECTS[i]['mails'] = int(SOUP('span', 'square')[i*3+1].contents[0])
    OBJECTS[i]['clics'] = int(SOUP('span', 'square')[i*3+2].contents[0])


# VUES
if FORCE_HEADER == 'True':
    print 'nom;prix;%s' % TIMESTAMP
else:
    print TIMESTAMP
for i, obj in enumerate(OBJECTS):
    if FORCE_HEADER == 'True':
        print '%s;%s;%s' % (OBJECTS[i]['title'], OBJECTS[i]['price'], OBJECTS[i]['vues'])
    else:
        print '%s' % OBJECTS[i]['vues']

print ''

# CLICS
if FORCE_HEADER == 'True':
    print 'nom;prix;%s' % TIMESTAMP
else:
    print TIMESTAMP
for i, obj in enumerate(OBJECTS):
    if FORCE_HEADER == 'True':
        print '%s;%s;%s' % (OBJECTS[i]['title'], OBJECTS[i]['price'], OBJECTS[i]['clics'])
    else:
        print '%s' % OBJECTS[i]['clics']

print ''

# MAILS
if FORCE_HEADER == 'True':
    print 'nom;prix;%s' % TIMESTAMP
else:
    print TIMESTAMP
for i, obj in enumerate(OBJECTS):
    if FORCE_HEADER == 'True':
        print '%s;%s;%s' % (OBJECTS[i]['title'], OBJECTS[i]['price'], OBJECTS[i]['mails'])
    else:
        print '%s' % OBJECTS[i]['mails']


# Nettoyage
remove(TMP_PAGE_FILE)
