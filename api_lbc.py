#!/usr/bin/env python
#-*- coding: utf-8 -*-
""" This script can get informations from website LeBonCoin """

# Standard library imports
from __future__ import print_function
from argparse import ArgumentParser
from collections import OrderedDict
from datetime import datetime
from getpass import getpass
from os import remove, path
from pickle import load, dump
from sys import argv
from time import time
# Related third party imports
from bs4 import BeautifulSoup
from requests import Session
from requests.utils import dict_from_cookiejar, cookiejar_from_dict

def get_timestamp():
    """ Return a timestamp """
    actual_time = time()
    timestamp = datetime.fromtimestamp(actual_time).strftime('%Y%m%d%H%M%S')
    return timestamp

class LeBonCoin(object):
    """ Utils class for api_lbc """
    def __init__(self, csv_root_path, verbose=False, uncolor=False):
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
        if not uncolor:
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

    def authentication(self, force=False):
        """ Authentication """
        if path.isfile(self.cookie_jar_path) and not force:
            with open(self.cookie_jar_path) as cookie_jar_file:
                cookies = cookiejar_from_dict(load(cookie_jar_file))
                self.profile['session'].cookies = cookies
        else:
            # Thank you, python2-3 team, for making such a fantastic mess with
            # input/raw_input :-)
            real_raw_input = vars(__builtins__).get('raw_input', input)
            self.profile['username'] = real_raw_input('Username: ')
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
        if req_url.status_code == 404:
            return False
        with open(self.tmp_html_path, 'wb') as tmp_html_file:
            tmp_html_file.write(req_url.text.encode('utf-8'))
        return True


    def get_ad(self, ad_id, ad_category):
        """ Display an ad information. """
        ad_list = {}
        ad_list['url'] = 'https://www.leboncoin.fr/%s/%s.htm?ca=12_s' % (ad_category, ad_id)
        ad_list['category'] = ad_category
        ad_list['id'] = ad_id

        if not self.download_web_page(ad_list['url']):
            print('%sThis ad may not exist...%s' % (self.colors['red'], self.colors['native']))
            return {}
        # Generate a soup
        with open(self.tmp_html_path, 'r') as tmp_html_file:
            soup = BeautifulSoup(tmp_html_file.read(), 'lxml')

        ad_list['description'] = soup.find('p', 'value', 'description').text
        ad_list['title'] = soup.find('button', 'share twitter trackable').attrs['data-text']
        try:
            ad_list['price'] = soup.find('h2', 'item_price')['content']
        except TypeError:
            ad_list['price'] = 0
        ad_list['address'] = soup.find('div', 'line line_city').find(
            'span', 'value').string.split('\n')[0]

        # Cleaning
        remove(self.tmp_html_path)

        return ad_list


    def get_dashboard(self):
        """ This method displays and writes infos of any ads. """
        self.download_web_page('https://compteperso.leboncoin.fr/account/index.html?ca=12_s')

        # Generate a soup
        with open(self.tmp_html_path, 'r') as tmp_html_file:
            soup = BeautifulSoup(tmp_html_file.read(), 'lxml')

        # Create a list of ads
        ads_list = {}
        for i, ad_soup in enumerate(soup('div', 'detail')):
            ad_dict = {}
            ad_dict['url'] = ad_soup.a.attrs['href']
            ad_dict['category'] = ad_dict['url'].split('/')[3]
            ad_dict['id'] = ad_dict['url'].split('/')[4].split('.')[0]
            ad_dict['title'] = ad_soup.a.string
            try:
                ad_dict['price'] = int(ad_soup.find('div', 'price').string.encode(
                    'utf-8').replace(' \xe2\x82\xac', ''))
            except AttributeError:
                ad_dict['price'] = 0
            ad_dict['views'] = -1
            ad_dict['mails'] = -1
            ad_dict['clics'] = -1
            ads_list[i] = ad_dict

        # Add views, mails and clics to the ads
        for i, ad_dict in enumerate(ads_list):
            ads_list[i]['views'] = int(soup('span', 'square')[i*3].contents[0])
            ads_list[i]['mails'] = int(soup('span', 'square')[i*3+1].contents[0])
            ads_list[i]['clics'] = int(soup('span', 'square')[i*3+2].contents[0])

        # Sort the list
        ads_list_sorted = OrderedDict(sorted(ads_list.items(), reverse=True))

        # Cleaning
        remove(self.tmp_html_path)

        return ads_list_sorted


    def get_search(self, keywords, filters):
        """ Search something on LBC. """
        if filters['localisation'] is None:
            localisation_url = ''
        else:
            localisation_url = '%s/' % filters['localisation']
        self.download_web_page(
            'https://www.leboncoin.fr/annonces/offres/%s/%s?sp=%s&q=%s&it=%s'
            % (filters['region'], localisation_url, int(filters['sort_by_price']),
               keywords, int(filters['search_in_title'])))

        # Generate a soup
        with open(self.tmp_html_path, 'r') as tmp_html_file:
            soup = BeautifulSoup(tmp_html_file.read(), 'lxml')

        # Cleaning
        remove(self.tmp_html_path)

        ads_list = {}
        for i, ad_soup in enumerate(soup('a', 'list_item')):
            ad_dict = {}
            try:
                ad_dict['category'] = ad_soup.attrs['href'].split('/')[3]
                ad_dict['id'] = ad_soup.attrs['href'].split('/')[4].split('.')[0]
                ad_dict['title'] = ad_soup.attrs['title']
            except IndexError:
                break
            try:
                ad_dict['price'] = ad_soup.h3.attrs['content']
            except AttributeError:
                ad_dict['price'] = 0
            except KeyError:
                ad_dict['price'] = 0
            ad_dict['address'] = ad_soup.find('meta').attrs['content']
            ads_list[i] = ad_dict

        return ads_list


    ###################
    ##    DISPLAY    ##
    ###################

    def display_ad(self, ad_id, ad_category):
        """ Display an ad. """
        ad_list = self.get_ad(ad_id, ad_category)
        if ad_list == {}:
            return False
        # Display informations
        print('%s%s%s ( %s%s €%s ) :' % (\
            self.colors['purple'], ad_list['title'].encode('utf-8'),\
            self.colors['native'], self.colors['green'], ad_list['price'],
            self.colors['native']))
        print('  Adresse: %s%s%s' %  (self.colors['bold'],
                                      ad_list['address'],
                                      self.colors['native']))
        print('  Catégorie: %s' %  ad_list['category'])
        print('  ID: %s' % ad_list['id'])
        print('  Description:')
        print(ad_list['description'].encode('utf-8'))
        print(self.colors['native'])

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
            print('%s%s%s ( %s%s €%s ) :' % (\
                self.colors['purple'], ads_list[i]['title'].encode('utf-8'),\
                self.colors['native'], self.colors['green'], ads_list[i]['price'],
                self.colors['native']))
            print('  Vues: %s%s%s' % (self.colors['bold'],\
                                       ads_list[i]['views'],\
                                       self.colors['native']))
            print('  Clics: %s%s%s' % (self.colors['bold'],\
                                       ads_list[i]['clics'],\
                                       self.colors['native']))
            print('  Mails: %s%s%s' % (self.colors['bold'],\
                                       ads_list[i]['mails'],\
                                       self.colors['native']))
            print('  ID: %s' % ads_list[i]['id'])
            print('  Catégorie: %s' % ads_list[i]['category'])

    def display_search(self, keywords, filters=None):
        """ Display the results of the search. """
        filters_dict = {'region': 'ile_de_france',
                        'localisation': None,
                        'price_min': 0,
                        'price_max': 999999,
                        'sort_by_price': False,
                        'search_in_title': False}
        filters_dict.update(filters)
        ads_list = self.get_search(keywords, filters_dict)
        for i in ads_list:
            if int(ads_list[i]['price']) >= filters_dict['price_min'] \
               and filters_dict['price_max'] >= int(ads_list[i]['price']):
                print('%s%s%s ( %s%s €%s ) :' % (\
                    self.colors['purple'], ads_list[i]['title'].encode('utf-8'),\
                    self.colors['native'], self.colors['green'], ads_list[i]['price'],
                    self.colors['native']))
                print('  Adresse: %s%s%s' %  (self.colors['bold'],
                                              ads_list[i]['address'].encode('utf-8'),
                                              self.colors['native']))
                print('  Catégorie: %s' %  ads_list[i]['category'])
                print('  ID: %s' % ads_list[i]['id'])

if __name__ == '__main__':
    CSV_ROOT_PATH = '.'
    PARSER = ArgumentParser()

    SUBPARSERS = PARSER.add_subparsers(help='commands')

    # A dashboard command
    DASHBOARD_PARSER = SUBPARSERS.add_parser('dashboard', help='List dashboard informations')
    DASHBOARD_PARSER.add_argument('--force-authentication', '-f', action='store_true',
                                  default=False, help='To force the authentication.')
    DASHBOARD_PARSER.add_argument('--uncolor', default=False, action='store_true',
                                  help='Disable coloration')

    # An ad command
    AD_PARSER = SUBPARSERS.add_parser('ad', help='Display a particulary ad')
    AD_PARSER.add_argument('id', action='store', help='ID of the ad')
    AD_PARSER.add_argument('category', action='store',
                           help='Category of the ad')
    AD_PARSER.add_argument('--uncolor', default=False, action='store_true',
                           help='Disable coloration')

    # A delete command
    SEARCH_PARSER = SUBPARSERS.add_parser('search', help='Search ads')
    SEARCH_PARSER.add_argument('keywords', action='store', help='Keywords of the search')
    SEARCH_PARSER.add_argument('--localisation', '-l', default=None, action='store',
                               help='Choose a particular localisation')
    SEARCH_PARSER.add_argument('--price-max', default=999999, action='store',
                               help='Set a max price')
    SEARCH_PARSER.add_argument('--price-min', default=0, action='store',
                               help='Set a in price')
    SEARCH_PARSER.add_argument('--uncolor', default=False, action='store_true',
                               help='Disable coloration')
    SEARCH_PARSER.add_argument('--search-in-title', default=False, action='store_true',
                               help='Search keywords only in the ad\'s title')
    SEARCH_PARSER.add_argument('--sort-by-price', default=False, action='store_true',
                               help='BETA: Sort list by price')

    ARGS = PARSER.parse_args()

    LBC = LeBonCoin(CSV_ROOT_PATH, uncolor=ARGS.uncolor)

    if argv[1] == 'dashboard':
        LBC.authentication(force=ARGS.force_authentication)
        LBC.display_dashboard()
    elif argv[1] == 'ad':
        LBC.display_ad(ARGS.id, ARGS.category)
    elif argv[1] == 'search':
        LBC.display_search(ARGS.keywords, filters={'localisation': ARGS.localisation,
                                                   'price_min': int(ARGS.price_min),
                                                   'price_max': int(ARGS.price_max),
                                                   'sort_by_price': ARGS.sort_by_price,
                                                   'search_in_title': ARGS.search_in_title})
