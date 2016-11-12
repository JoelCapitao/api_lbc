#!/usr/bin/python2.7
#-*- coding: utf-8 -*-
""" This script can get informations from website LeBonCoin """

# from pdb import set_trace as st
from argparse import ArgumentParser
from collections import OrderedDict
from datetime import datetime
from getpass import getpass
from os import remove, path
from pickle import load, dump
from time import time
from requests import Session
from requests.utils import dict_from_cookiejar, cookiejar_from_dict
import bs4 as BeautifulSoup

def get_timestamp():
    """ Return a timestamp """
    actual_time = time()
    timestamp = datetime.fromtimestamp(actual_time).strftime('%Y%m%d%H%M%S')
    return timestamp

class LeBonCoin(object):
    """ Utils class for api_lbc """
    def __init__(self, csv_root_path):
        """ init"""
        self.tmp_html_path = './tmp_page.html'
        self.cookie_jar_path = '/tmp/cookie_api_lbc.jar'
        self.username = ''
        self.password = ''
        self.csv_root_path = csv_root_path
        self.timestamp = get_timestamp()
        self.session = Session()

    def authentication(self):
        """ Authentication """
        if path.isfile(self.cookie_jar_path):
            with open(self.cookie_jar_path) as cookie_jar_file:
                cookies = cookiejar_from_dict(load(cookie_jar_file))
                self.session.cookies = cookies
        else:
            self.username = raw_input('Username: ')
            self.password = getpass()
            self.cookie_gen()

    def cookie_gen(self):
        """This method generate an authentication cookie. It follow the current
        session, but it's also save in self.cookie_jar_path."""
        url = 'https://compteperso.leboncoin.fr/store/verify_login/0'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'st_username': self.username, 'st_passwd': self.password}
        self.session.post(url, headers=headers, data=payload)
        with open(self.cookie_jar_path, 'w') as cookie_jar_file:
            dump(dict_from_cookiejar(self.session.cookies), cookie_jar_file)

    def download_web_page(self, url):
        """ This method download a web page and store the informations
        in self.tmp_html_path """
        req_url = self.session.get(url)
        with open(self.tmp_html_path, 'wb') as tmp_html_file:
            tmp_html_file.write(req_url.text.encode('utf-8'))

    def get_dashboard(self):
        """ This method displays and writes infos of any ads. """
        self.download_web_page('https://compteperso.leboncoin.fr/account/index.html?ca=12_s')

        # Generation of the list
        tmp_html_file = open(self.tmp_html_path, 'r')
        soup = BeautifulSoup.BeautifulSoup(tmp_html_file.read(), 'lxml')
        tmp_html_file.close()

        ads_list = {}
        for i, title in enumerate(soup.find_all('div', 'title')):
            ad_dict = {}
            ad_dict['url'] = title.a.attrs['href']
            ad_dict['category'] = ad_dict['url'].split('/')[3]
            ad_dict['id'] = ad_dict['url'].split('/')[4].split('.')[0]
            ad_dict['title'] = title.a.string
            ad_dict['price'] = -1
            ad_dict['views'] = -1
            ad_dict['mails'] = -1
            ad_dict['clics'] = -1
            ads_list[i] = ad_dict

        for i, price in enumerate(soup.find_all('div', 'price')):
            ads_list[i]['price'] = \
            int(price.contents[0].encode('utf-8').replace(' \xe2\x82\xac', ''))

        for i, ad_dict in enumerate(ads_list):
            ads_list[i]['views'] = int(soup('span', 'square')[i*3].contents[0])
            ads_list[i]['mails'] = int(soup('span', 'square')[i*3+1].contents[0])
            ads_list[i]['clics'] = int(soup('span', 'square')[i*3+2].contents[0])

        # Sort the list of ads
        ads_list_sorted = OrderedDict(sorted(ads_list.items(), reverse=True))

        # Write ad info in file
        for i in ads_list_sorted:
            csv_ad_path = '%s/%s.csv' % (self.csv_root_path, ads_list_sorted[i]['title'])
            if not path.isfile(csv_ad_path):
                csv_ad_file = open(csv_ad_path, 'w')
                csv_ad_file.write('timestamp;price;views;clics;mails;\n')
            else:
                csv_ad_file = open(csv_ad_path, 'a')
            csv_ad_file.write('%s;%s;%s;%s;%s;\n' % (\
                self.timestamp,\
                ads_list_sorted[i]['price'],\
                ads_list_sorted[i]['views'],\
                ads_list_sorted[i]['clics'],\
                ads_list_sorted[i]['mails']))
            csv_ad_file.close()

        # Display informations
        for i in ads_list_sorted:
            print '%s ( %s € ) :' % (\
                ads_list_sorted[i]['title'].encode('utf-8'),\
                ads_list_sorted[i]['price'])
            print '  Category: %s' % ads_list_sorted[i]['category']
            print '  ID: %s' % ads_list_sorted[i]['id']
            print '  views: %s' % ads_list_sorted[i]['views']
            print '  clics: %s' % ads_list_sorted[i]['clics']
            print '  mails: %s' % ads_list_sorted[i]['mails']

        # Cleaning
        remove(self.tmp_html_path)


if __name__ == '__main__':
    PARSER = ArgumentParser()
    PARSER.add_argument('--show',
                        metavar='[ID]',
                        nargs=1,
                        help='Show all ads or just one')
    ARGS = PARSER.parse_args()

    CSV_ROOT_PATH = '.'

    if ARGS.show is not None:
        if ARGS.show[0] == 'all':
            LBC = LeBonCoin(CSV_ROOT_PATH)
            LBC.authentication()
            LBC.get_dashboard()
        else:
            print 'Not implemented yet.'
