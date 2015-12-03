#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import sys
from pdb import set_trace as st
import subprocess
import bs4 as BeautifulSoup
import re
import time
import datetime

username = sys.argv[1]
password = sys.argv[2]
force_header = sys.argv[3]
cookie_jar = './cookie_api_lbc.jar'

ts = time.time()
timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d%H%M%S')

page_filename = './page.html'

popen = subprocess.Popen(('./page_gen.sh', username, password, page_filename), stdout=subprocess.PIPE)
popen.wait()

f = open('./page.html', 'r')
soup = BeautifulSoup.BeautifulSoup(f.read(), 'lxml')
f.close()

objects = {}
for i, title in enumerate(soup.find_all('div', 'title')):
    o = {}
    o['title'] = str(title.a.contents[0].encode('utf-8').decode('ascii', 'ignore'))
    objects[i] = o

for i, price in enumerate(soup.find_all('div', 'price')):
    objects[i]['price'] = int(price.contents[0].encode('utf-8').replace(' \xe2\x82\xac', ''))

for i in range(len(objects)):
    objects[i]['vues'] = int(soup('span', 'square')[i*3].contents[0])
    objects[i]['mails'] = int(soup('span', 'square')[i*3+1].contents[0])
    objects[i]['clics'] = int(soup('span', 'square')[i*3+2].contents[0])


# VUES
if force_header == 'True':
    print 'nom;prix;%s' % timestamp
else:
    print timestamp
for i in range(len(objects)):
    if force_header == 'True':
        print '%s;%s;%s' % (objects[i]['title'], objects[i]['price'], objects[i]['vues'])
    else:
        print '%s' % objects[i]['vues']

print ''

# CLICS
if force_header == 'True':
    print 'nom;prix;%s' % timestamp
else:
    print timestamp
for i in range(len(objects)):
    if force_header == 'True':
        print '%s;%s;%s' % (objects[i]['title'], objects[i]['price'], objects[i]['clics'])
    else:
        print '%s' % objects[i]['clics']

print ''

# MAILS
if force_header == 'True':
    print 'nom;prix;%s' % timestamp
else:
    print timestamp
for i in range(len(objects)):
    if force_header == 'True':
        print '%s;%s;%s' % (objects[i]['title'], objects[i]['price'], objects[i]['mails'])
    else:
        print '%s' % objects[i]['mails']