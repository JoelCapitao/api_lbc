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

import cookielib
import requests
import pickle
import getpass

try:
    USERNAME = argv[1]
    CSV_PATH = argv[2]
except IndexError:
    print '%s USERNAME CSV_PATH' % argv[0]
    exit(1)

def get_timestamp():
    """ Return a timestamp """
    actual_time = time()
    timestamp = datetime.fromtimestamp(actual_time).strftime('%Y%m%d%H%M%S')
    return timestamp

class LeBonCoin(object):
    """ Utils class for api_lbc """
    def __init__(self, username, csv_root_path):
        """ init"""
        self.tmp_html_path = './tmp_page.html'
        self.cookie_jar_path = '/tmp/cookie_api_lbc.jar'
        self.username = username
        self.password = ''
        self.csv_root_path = csv_root_path
        self.timestamp = get_timestamp()
        self.session = requests.Session()

    def authentication(self):
        """ Authentication """
        if path.isfile(self.cookie_jar_path):
            with open(self.cookie_jar_path) as cookie_jar_file:
                cookies = requests.utils.cookiejar_from_dict(pickle.load(cookie_jar_file))
                self.session.cookies = cookies
        else:
            print 'Veuillez entrer votre mot de passe : '
            self.password = getpass.getpass()
            self.cookie_gen()

    def cookie_gen(self):
        """cookie gen"""
        url = 'https://compteperso.leboncoin.fr/store/verify_login/0'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'st_username': self.username, 'st_passwd': self.password}
        self.session.post(url, headers=headers, data=payload)
        with open(self.cookie_jar_path, 'w') as cookie_jar_file:
            pickle.dump(requests.utils.dict_from_cookiejar(self.session.cookies), cookie_jar_file)

    def download_web_page(self, url):
        """ This method download a web page and store the informations
        in self.tmp_html_path """
        req_url = self.session.get(url)
        with open(self.tmp_html_path, 'wb') as tmp_html_file:
            tmp_html_file.write(req_url.text.encode('utf-8'))

    def get_dashboard(self):
        """ get_dashboard """
        self.download_web_page('https://compteperso.leboncoin.fr/account/index.html?ca=12_s')

        tmp_html_file = open(self.tmp_html_path, 'r')
        soup = BeautifulSoup.BeautifulSoup(tmp_html_file.read(), 'lxml')
        tmp_html_file.close()

        # Generation of the list
        ads_list = {}
        for i, title in enumerate(soup.find_all('div', 'title')):
            o = {}
            o['url'] = title.a.attrs['href']
            o['title'] = title.a.string
            print o['title']
            # o['title'] = str(title.a.contents[0].encode('utf-8').decode('ascii', 'ignore'))
            o['price'] = -1
            o['views'] = -1
            o['mails'] = -1
            o['clics'] = -1
            ads_list[i] = o

        for i, price in enumerate(soup.find_all('div', 'price')):
            ads_list[i]['price'] = int(price.contents[0].encode('utf-8').replace(' \xe2\x82\xac', ''))

        for i, o in enumerate(ads_list):
            ads_list[i]['views'] = int(soup('span', 'square')[i*3].contents[0])
            ads_list[i]['mails'] = int(soup('span', 'square')[i*3+1].contents[0])
            ads_list[i]['clics'] = int(soup('span', 'square')[i*3+2].contents[0])

        # Changement de l'ordre
        ads_list_sorted = OrderedDict(sorted(ads_list.items(), reverse=True))

        for o in ads_list_sorted:
            csv_ad_path = '%s/%s.csv' % (self.csv_root_path, ads_list_sorted[o]['title'])
            if not path.isfile(csv_ad_path):
                csv_ad_file = open(csv_ad_path, 'w')
                csv_ad_file.write('timestamp;price;views;clics;mails;\n')
            else:
                csv_ad_file = open(csv_ad_path, 'a')
            csv_ad_file.write('%s;%s;%s;%s;%s;\n' % (self.timestamp, ads_list_sorted[o]['price'], ads_list_sorted[o]['views'], ads_list_sorted[o]['clics'], ads_list_sorted[o]['mails']))
            csv_ad_file.close()

        # Cleaning
        remove(self.tmp_html_path)

LBC = LeBonCoin(USERNAME, CSV_PATH)
LBC.authentication()
# LBC.cookie_gen()

LBC.get_dashboard()
