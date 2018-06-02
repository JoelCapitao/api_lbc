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
from time import time, mktime
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

    def authentication(self, username=None, force=False):
        """ Authentication """
        if path.isfile(self.cookie_jar_path) and not force:
            with open(self.cookie_jar_path) as cookie_jar_file:
                cookies = cookiejar_from_dict(load(cookie_jar_file))
                timestamp_now = mktime(datetime.utcnow().timetuple())
                if int(cookies['token_expire']) > timestamp_now:
                    self.profile['session'].cookies = cookies
                else:
                    force = True
        if not path.isfile(self.cookie_jar_path) or force:
            # Thank you, python2-3 team, for making such a fantastic mess with
            # input/raw_input :-)
            real_raw_input = vars(__builtins__).get('raw_input', input)
            if username is None:
                self.profile['username'] = real_raw_input('Username: ')
            else:
                self.profile['username'] = username
            self.profile['password'] = getpass()
            self.cookie_gen()

    def cookie_gen(self):
        """This method generate an authentication cookie. It follow the current
        session, but it's also save in self.cookie_jar_path."""
        url = 'https://compteperso.leboncoin.fr/store/verify_login/0'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'st_username': self.profile['username'], 'st_passwd': self.profile['password']}
        req_url = self.profile['session'].post(url, headers=headers, data=payload)
        # Generate a soup
        soup = BeautifulSoup(req_url.text, 'lxml')
        if soup.find('span', 'error'):
            print('Authentication failed...')
        else:
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


    def get_ad(self, ad_key):
        """ Display an ad information. """
        ad_list = {}
        ad_list['id'] = ad_key.split(':')[0]
        ad_list['category'] = ad_key.split(':')[1]
        ad_list['url'] = 'https://www.leboncoin.fr/%s/%s.htm?ca=12_s' \
            % (ad_list['category'], ad_list['id'])

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


    def get_search(self, keywords, filters, page_num=1):
        """ Search something on LBC. """

        if filters['category'] == 'ventes_immobilieres':
            region = '' if filters['region'] is None else '%s/' % filters['region']
            location_url = '' if filters['location'] is None else filters['location']
            price_min = '' if filters['price_min'] is None else '&ps=%s' % (filters['price_min'] / 25000)
            price_max = '' if filters['price_max'] is None else '&pe=%s' % (filters['price_max'] / 25000)
            surface_min = '' if filters['surface_min'] is None else '&sqs=%s' % filters['surface_min']
            surface_max = '' if filters['surface_max'] is None else '&sqe=%s' % filters['surface_max']
            room_min = '' if filters['room_min'] is None else '&ros=%s' % filters['room_min']
            room_max = '' if filters['room_max'] is None else '&roe=%s' % filters['room_max']
            property_type = '&ret=2'

            self.download_web_page(
                'https://www.leboncoin.fr/ventes_immobilieres/offres/%s?th=1&location=%s%s%s%s%s%s%s%s'
                % (region, location_url, price_min, price_max, surface_min, surface_max, room_min,
                   room_max, property_type))
        else:
            self.download_web_page(
                'https://www.leboncoin.fr/annonces/offres/%s/%s?sp=%s&q=%s&it=%s&o=%s'
                % (filters['region'], location_url, int(filters['sort_by_price']),
                   keywords, int(filters['search_in_title']), page_num))

        # Generate a soup
        with open(self.tmp_html_path, 'r') as tmp_html_file:
            soup = BeautifulSoup(tmp_html_file.read(), 'lxml')

        # Cleaning
        remove(self.tmp_html_path)

        ads_list = {}
        for ad_soup in soup('a', 'list_item'):
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
            ads_list[ad_dict['id']] = ad_dict

        return ads_list


    ###################
    ##    DISPLAY    ##
    ###################

    def display_ad(self, ad_key):
        """ Display an ad. """
        ad_list = self.get_ad(ad_key)
        if ad_list == {}:
            return False
        # Display informations
        print('%s%s%s ( %s%s €%s ) :' % (\
            self.colors['purple'], ad_list['title'].encode('utf-8'),\
            self.colors['native'], self.colors['green'], ad_list['price'],
            self.colors['native']))
        print('  Adresse: %s%s%s' % (self.colors['bold'],
                                     ad_list['address'],
                                     self.colors['native']))
        print('  URL: %s%s%s' % (self.colors['bold'],
                                 ad_list['url'],
                                 self.colors['native']))
        print('  Key: %s:%s' % (ad_list['id'], ad_list['category']))
        print('  Description:')
        print(ad_list['description'].encode('utf-8'))
        print(self.colors['native'])
        return True

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
            print('  Key: %s:%s' % (ads_list[i]['id'], ads_list[i]['category']))

    def display_search(self, keywords, filters=None):
        """ Display the results of the search. """
        filters_dict = {'category': None,
                        'location': None,
                        'price_max': 999999,
                        'price_min': 0,
                        'property_type': None,
                        'region': None,
                        'room_max': None,
                        'room_min': None,
                        'search_in_title': False,
                        'sort_by_price': False,
                        'surface_max': None,
                        'surface_min': None}
        filters_dict.update(filters)
        ads_list = {}
        for page in range(3):
            ads_list.update(self.get_search(keywords, filters_dict, page_num=page))
        for ad_id in ads_list:
            if int(ads_list[ad_id]['price']) >= filters_dict['price_min'] \
               and filters_dict['price_max'] >= int(ads_list[ad_id]['price']):
                print('%s%s%s ( %s%s €%s ) :' % (\
                    self.colors['purple'], ads_list[ad_id]['title'].encode('utf-8'),\
                    self.colors['native'], self.colors['green'], ads_list[ad_id]['price'],
                    self.colors['native']))
                print('  Adresse: %s%s%s' %  (self.colors['bold'],
                                              ads_list[ad_id]['address'].encode('utf-8'),
                                              self.colors['native']))
                print('  Key: %s:%s' % (ads_list[ad_id]['id'], ads_list[ad_id]['category']))

if __name__ == '__main__':
    CSV_ROOT_PATH = '.'
    PARSER = ArgumentParser()

    SUBPARSERS = PARSER.add_subparsers(help='commands')

    # A dashboard command
    DASHBOARD_PARSER = SUBPARSERS.add_parser('dashboard', help='List dashboard informations')
    DASHBOARD_PARSER.add_argument('--force-authentication', '-f', action='store_true',
                                  default=False, help='To force the authentication.')
    DASHBOARD_PARSER.add_argument('--username', '-u', action='store',
                                  default=None, help='Username to log in.')
    DASHBOARD_PARSER.add_argument('--uncolor', default=False, action='store_true',
                                  help='Disable coloration')

    # An ad command
    AD_PARSER = SUBPARSERS.add_parser('ad', help='Display a particulary ad')
    AD_PARSER.add_argument('key', action='store', help='ID:CATEGORY of the ad')
    AD_PARSER.add_argument('--uncolor', default=False, action='store_true',
                           help='Disable coloration')

    # A search command
    SEARCH_PARSER = SUBPARSERS.add_parser('search', help='Search ads')
    SEARCH_PARSER.add_argument('keywords', action='store', help='Keywords of the search')
    SEARCH_PARSER.add_argument('--category', '-c', default=None, action='store',
                               help='Set the category of the search')
    SEARCH_PARSER.add_argument('--location', '-l', default=None, action='store',
                               help='Choose a particular location')
    SEARCH_PARSER.add_argument('--price-max', default=999999, action='store',
                               help='Set a max price')
    SEARCH_PARSER.add_argument('--price-min', default=0, action='store',
                               help='Set a in price')
    SEARCH_PARSER.add_argument('--property-type', default=None, action='store_true',
                               help='Set the property type')
    SEARCH_PARSER.add_argument('--region', default='ile_de_france', action='store_true',
                               help='Set the region')
    SEARCH_PARSER.add_argument('--room-max', default=None, action='store_true',
                               help='Set the maximum number of rooms')
    SEARCH_PARSER.add_argument('--room-min', default=None, action='store_true',
                               help='Set the minimum number of rooms')
    SEARCH_PARSER.add_argument('--search-in-title', default=False, action='store_true',
                               help='Search keywords only in the ad\'s title')
    SEARCH_PARSER.add_argument('--sort-by-price', default=False, action='store_true',
                               help='BETA: Sort list by price')
    SEARCH_PARSER.add_argument('--surface-max', default=None, action='store_true',
                               help='Set a max surface')
    SEARCH_PARSER.add_argument('--surface-min', default=None, action='store_true',
                               help='Set a min surface')
    SEARCH_PARSER.add_argument('--uncolor', default=False, action='store_true',
                               help='Disable coloration')

    ARGS = PARSER.parse_args()

    LBC = LeBonCoin(CSV_ROOT_PATH, uncolor=ARGS.uncolor)

    if argv[1] == 'dashboard':
        LBC.authentication(username=ARGS.username, force=ARGS.force_authentication)
        LBC.display_dashboard()
    elif argv[1] == 'ad':
        LBC.display_ad(ARGS.key)
    elif argv[1] == 'search':
        LBC.display_search(ARGS.keywords, filters={'category': ARGS.category,
                                                   'location': ARGS.location,
                                                   'price_max': int(ARGS.price_max),
                                                   'price_min': int(ARGS.price_min),
                                                   'property_type': ARGS.property_type,
                                                   'region': ARGS.region,
                                                   'room_max': ARGS.room_max,
                                                   'room_min': ARGS.room_min,
                                                   'search_in_title': ARGS.search_in_title,
                                                   'sort_by_price': ARGS.sort_by_price,
                                                   'surface_max': ARGS.surface_max,
                                                   'surface_min': ARGS.surface_min,
                                                   'uncolor': int(ARGS.uncolor)})
