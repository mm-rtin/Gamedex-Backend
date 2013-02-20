"""searchSources.py: Third party search data sources: Steam, Metacritic, Amazon """

__author__ = "Michael Martin"
__status__ = "Production"

import urllib
import bottlenose
import logging
import StringIO
import gzip

from google.appengine.api import urlfetch
from google.appengine.api import memcache

from lxml.cssselect import CSSSelector
from lxml import etree

from management.keys import Keys

# amazon api properties
AMAZON_ACCESS_KEY = 'AMAZON_ACCESS_KEY'
AMAZON_SECRET_KEY = 'AMAZON_SECRET_KEY'
AMAZON_ASSOCIATE_TAG = 'codeco06-20'

# giantbomb api properties
GIANTBOMB_API_KEY = 'GIANTBOMB_API_KEY'


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Steam
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Steam():

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Search Steam
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def searchSteam(keywords):

        # http://store.steampowered.com/search/suggest?term=searchTerms&f=games
        # memcache key
        memcacheKey = 'steamTitle_' + keywords

        # return memcached search if available
        steamSearch = memcache.get(memcacheKey)

        if steamSearch is not None:
            logging.info('-------------- searchSteam CACHE HIT --------------')
            logging.info(memcacheKey)

            # return json
            return steamSearch

        else:

            logging.info('-------------- searchSteam MISS --------------')
            logging.info(memcacheKey)

            url = 'http://store.steampowered.com/search/suggest?f=games&term=' + urllib.quote_plus(keywords)

            # fetch - accept gzip (url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
            headers = {'Accept-Encoding': 'gzip'}
            response = urlfetch.fetch(url, None, 'GET', headers, False, False, 30)

            # decompress
            f = StringIO.StringIO(response.content)
            c = gzip.GzipFile(fileobj=f)
            content = c.read()

            searchList = Steam.parseSteamSearch(content)

        return searchList

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # PARSE STEAM RESULTS
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def parseSteamSearch(response):

        searchList = []

        try:
            html = etree.HTML(response)

            rowSel = CSSSelector('.match')
            nameSel = CSSSelector('.match_name')
            priceSel = CSSSelector('.match_price')

            for row in rowSel(html):

                try:
                    nameElement = nameSel(row)
                    priceElement = priceSel(row)

                    name = nameElement[0].text.strip()
                    price = priceElement[0].text.strip()
                    url = row.get('href')

                    steamObj = {'name': name, 'page': url, 'price': price}
                    searchList.append(steamObj)

                except IndexError:
                    logging.error('parseSteamSearch: IndexError')

        except:
            logging.error('parseSteamSearch: Parse Error')

        return searchList


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Amazon
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Amazon():

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # searchAmazon
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def searchAmazon(keywords, browseNode, responseGroup, searchIndex, page):

        amazon = bottlenose.Amazon(Keys.getKey(AMAZON_ACCESS_KEY), Keys.getKey(AMAZON_SECRET_KEY), AMAZON_ASSOCIATE_TAG)

        # memcache key
        memcacheKey = 'searchAmazon_' + keywords + '_' + browseNode + '_' + responseGroup + '_' + searchIndex + '_' + page

        # return memcached search if available
        search = memcache.get(memcacheKey)

        if search is not None:
            logging.info('')
            logging.info('-------------- searchAmazon CACHE HIT --------------')
            logging.info(memcacheKey)
            logging.info('')
            logging.info('')

            return search

        else:
            # Availability='Available', Condition='All', MerchantId='Amazon', MinimumPrice='800', MaximumPrice='13500'
            if browseNode == '0':
                response = amazon.ItemSearch(SearchIndex=searchIndex, Title=keywords, ResponseGroup=responseGroup, ItemPage=page, Sort='salesrank')
            else:
                response = amazon.ItemSearch(SearchIndex=searchIndex, Title=keywords, ResponseGroup=responseGroup, ItemPage=page, Sort='salesrank', MinimumPrice='800', MaximumPrice='13500', BrowseNode=browseNode)

            logging.info('')
            logging.info('-------------- searchAmazon MISS --------------')
            logging.info(memcacheKey)
            logging.info('')
            logging.info('')

            # cache amazon search for 1 day
            if not memcache.add(memcacheKey, response, 86400):
                logging.error('searchAmazon: Memcache set failed')
                logging.error(memcacheKey)

            return search

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # detailAmazon
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def detailAmazon(asin, responseGroup):

        memcacheKey = 'detailAmazon_' + asin + '_' + responseGroup

        # return memcached detail if available
        detail = memcache.get(memcacheKey)

        if detail is not None:
            logging.info('')
            logging.info('-------------- detailAmazon HIT --------------')
            logging.info(memcacheKey)
            logging.info('')
            logging.info('')

            return detail

        # get detail from source
        else:
            amazon = bottlenose.Amazon(Keys.getKey(AMAZON_ACCESS_KEY), Keys.getKey(AMAZON_SECRET_KEY), AMAZON_ASSOCIATE_TAG)
            response = amazon.ItemLookup(ItemId=asin, IdType='ASIN', ResponseGroup=responseGroup)

            logging.info('')
            logging.info('-------------- detailAmazon MISS --------------')
            logging.info(memcacheKey)
            logging.info('')
            logging.info('')

            # cache amazon detail for 1 day
            if not memcache.add(memcacheKey, response, 86400):
                logging.error('detailAmazon: Memcache set failed')
                logging.error(memcacheKey)

            return response


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Metacritic
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Metacritic():

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Search Metacritic
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def searchMetacritic(keywords, platform):

        # memcache key (cache with platform - so each platform gets its own score)
        memcacheKey = 'searchMetacritic_' + keywords + '_' + platform

        # return memcached search if available
        metacriticSearch = memcache.get(memcacheKey)

        if metacriticSearch is not None:
            logging.info('')
            logging.info('-------------- searchMetacritic CACHE HIT --------------')
            logging.info(memcacheKey)
            logging.info('')
            logging.info('')

            # return json
            return metacriticSearch

        else:

            logging.info('')
            logging.info('-------------- searchMetacritic MISS --------------')
            logging.info(memcacheKey)
            logging.info('')
            logging.info('')

            url = 'http://www.metacritic.com/search/game/' + urllib.quote_plus(keywords) + '/results'

            # fetch - accept gzip (url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
            headers = {'Accept-Encoding': 'gzip'}
            response = urlfetch.fetch(url, None, 'GET', headers, False, False, 30)

            # decompress
            f = StringIO.StringIO(response.content)
            c = gzip.GzipFile(fileobj=f)
            content = c.read()

        # return raw response html
        return content
