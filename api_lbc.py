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
    def __init__(self, csv_root_path, verbose=False, color=True):
        """ init"""
        self.tmp_html_path = './tmp_page.html'
        self.cookie_jar_path = '/tmp/cookie_api_lbc.jar'
        self.csv_root_path = csv_root_path
        self.timestamp = get_timestamp()
        self.profile = {
            'username': '',
            'password': '',
            'session': Session(),
            'verbose': verbose,
        }
        if color:
            self.colors = {
                'red': '\033[1;31m',
                'green': '\033[1;32m',
                'yellow': '\033[1;33m',
                'purple': '\033[1;34m',
                'pink': '\033[1;35m',
                'light_blue': '\033[1;36m',
                'white': '\033[m',
                'native': '\033[m',
                'bold': '\033[1m'
            }
        else:
            self.colors = {
                'red': '',
                'green': '',
                'yellow': '',
                'purple': '',
                'pink': '',
                'light_blue': '',
                'white': '',
                'native': '',
                'bold': ''
            }

    ########################
    ##   AUTHENTICATION   ##
    ########################

    def authentication(self):
        """ Authentication """
        if path.isfile(self.cookie_jar_path):
            with open(self.cookie_jar_path) as cookie_jar_file:
                cookies = cookiejar_from_dict(load(cookie_jar_file))
                self.profile['session'].cookies = cookies
        else:
            self.profile['username'] = raw_input('Username: ')
            self.profile['password'] = getpass()
            self.cookie_gen()

    def cookie_gen(self):
        """This method generate an authentication cookie. It follow the current
        session, but it's also save in self.cookie_jar_path."""
        url = 'https://compteperso.leboncoin.fr/store/verify_login/0'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'st_username': self.profile['username'], 'st_passwd': self.profile['password']}
        self.profile['session'].post(url, headers=headers, data=payload)
        with open(self.cookie_jar_path, 'w') as cookie_jar_file:
            dump(dict_from_cookiejar(self.profile['session'].cookies), cookie_jar_file)


    ###################
    ##   FORMATTER   ##
    ###################

    def download_web_page(self, url):
        """ This method download a web page and store the informations
        in self.tmp_html_path """
        req_url = self.profile['session'].get(url)
        with open(self.tmp_html_path, 'wb') as tmp_html_file:
            tmp_html_file.write(req_url.text.encode('utf-8'))

    def get_ad(self, ad_id):
        """ Display an ad information. """
        ads_list = self.get_dashboard()
        ad_list = {}
        for ad_list_tmp in ads_list.values():
            if ad_list_tmp['id'] == ad_id:
                ad_list = ad_list_tmp

        if ad_list == {}:
            print '%sError. This ID (%s) does not exist.%s' % (self.colors['red'],
                                                               ad_id,
                                                               self.colors['native'])
            return ad_list

        self.download_web_page(ad_list['url'])
        # Generation of the list
        tmp_html_file = open(self.tmp_html_path, 'r')
        soup = BeautifulSoup.BeautifulSoup(tmp_html_file.read(), 'lxml')
        tmp_html_file.close()

        ad_list['description'] = soup('p', 'value', 'description')[0].text

        return ad_list


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

        # Cleaning
        remove(self.tmp_html_path)

        return ads_list_sorted


    ###################
    ##    DISPLAY    ##
    ###################

    def display_ad(self, ad_id):
        """ Display an ad. """
        ad_list = self.get_ad(ad_id)
        if ad_list == {}:
            return False
        # Display informations
        print '%s%s%s ( %s € ) :' % (\
            self.colors['bold'], ad_list['title'].encode('utf-8'),\
            self.colors['native'], ad_list['price'])
        if self.profile['verbose']:
            print '  Category: %s' %  ad_list['category']
            print '  ID: %s' % ad_list['id']
        print '  views: %s%s%s' % (self.colors['bold'],\
                                   ad_list['views'],\
                                   self.colors['native'])
        print '  clics: %s%s%s' % (self.colors['bold'],\
                                   ad_list['clics'],\
                                   self.colors['native'])
        print '  mails: %s%s%s' % (self.colors['bold'],\
                                   ad_list['mails'],\
                                   self.colors['native'])
        print '  Description:'
        print ad_list['description'].encode('utf-8')
        print self.colors['native']

    def display_dashboard(self):
        """ Display a dashboard. """
        ads_list = self.get_dashboard()
        # Write ad info in file
        for i in ads_list:
            csv_ad_path = '%s/%s.csv' % (self.csv_root_path, ads_list[i]['title'])
            if not path.isfile(csv_ad_path):
                csv_ad_file = open(csv_ad_path, 'w')
                csv_ad_file.write('timestamp;price;views;clics;mails;\n')
            else:
                csv_ad_file = open(csv_ad_path, 'a')
            csv_ad_file.write('%s;%s;%s;%s;%s;\n' % (\
                self.timestamp,\
                ads_list[i]['price'],\
                ads_list[i]['views'],\
                ads_list[i]['clics'],\
                ads_list[i]['mails']))
            csv_ad_file.close()

        # Display informations
        for i in ads_list:
            print '%s%s%s ( %s € ) :' % (\
                self.colors['bold'], ads_list[i]['title'].encode('utf-8'),\
                self.colors['native'], ads_list[i]['price'])
            print '  ID: %s%s%s' % (self.colors['bold'],\
                                    ads_list[i]['id'],\
                                    self.colors['native'])
            print '  views: %s%s%s' % (self.colors['bold'],\
                                       ads_list[i]['views'],\
                                       self.colors['native'])
            print '  clics: %s%s%s' % (self.colors['bold'],\
                                       ads_list[i]['clics'],\
                                       self.colors['native'])
            print '  mails: %s%s%s' % (self.colors['bold'],\
                                       ads_list[i]['mails'],\
                                       self.colors['native'])
            if self.profile['verbose']:
                print '  Category: %s' % ads_list[i]['category']



if __name__ == '__main__':
    CSV_ROOT_PATH = '.'
    PARSER = ArgumentParser()

    PARSER.add_argument('--show',
                        metavar='[ID]',
                        nargs=1,
                        help='Show all ads or just one')
    PARSER.add_argument('--verbose',
                        action='store_true',
                        default=False,
                        help='Enable verbose mode')
    PARSER.add_argument('--uncolor',
                        action='store_false',
                        default=True,
                        help='Disable color mode')
    ARGS = PARSER.parse_args()

    LBC = LeBonCoin(CSV_ROOT_PATH, verbose=ARGS.verbose, color=ARGS.uncolor)
    LBC.authentication()

    if ARGS.show is not None:
        if ARGS.show[0] == 'all':
            LBC.display_dashboard()
        else:
            LBC.display_ad(ARGS.show[0])
