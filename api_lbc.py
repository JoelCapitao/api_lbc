#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

import sys
from pdb import set_trace as st
import subprocess
import bs4 as BeautifulSoup
import re

username = sys.argv[1]
password = sys.argv[2]
cookie_jar = './cookie_api_lbc.jar'

popen = subprocess.Popen(('./page_gen.sh', username, password), stdout=subprocess.PIPE)

popen.wait()

f = open('./page.html', 'r')
soup = BeautifulSoup.BeautifulSoup(f.read(), 'lxml')
f.close()

objects = {}
for i, title in enumerate(soup.find_all('div', 'title')):
    o = {}
    o['title'] = title.a.contents[0]
    objects[i] = o

for i, price in enumerate(soup.find_all('div', 'price')):
    objects[i]['price'] = int(price.contents[0].encode('utf-8').replace(' \xe2\x82\xac', ''))

for i in range(len(objects)):
    objects[i]['vues'] = int(soup("span", "square")[i*3].contents[0])
    objects[i]['mails'] = int(soup("span", "square")[i*3+1].contents[0])
    objects[i]['clics'] = int(soup("span", "square")[i*3+2].contents[0])

st()
# grep -a 'class="title"' page.html  | awk -F '12_s">' '{print $2}' | awk -F '</a>' '{print $1}'
