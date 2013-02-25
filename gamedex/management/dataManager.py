"""dataManager.py: Methods for peridically updating main application datastore """

__author__ = "Michael Martin"
__status__ = "Production"


import logging
import StringIO
import gzip
import difflib

from google.appengine.api import urlfetch
from google.appengine.ext import deferred

from django.http import HttpResponse

from lxml.cssselect import CSSSelector
from lxml import etree

from models import Items
from services.searchSources import Steam

# constants
METACRITIC_BASE_URL = 'http://www.metacritic.com'


# UPDATE STEAM PRICE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateSteamPrice(request):

    deferred.defer(updateSteamPriceDeferred)

    return HttpResponse('success', mimetype='text/plain', status='200')


# UPDATE STEAM PRICE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateSteamPriceDeferred():

    # get items
    items = Items.query().fetch()

    # iterate items
    for item in items:

        # steam price URL found
        if (item.item_steamPriceURL != None and item.item_steamPriceURL.strip() != ''):

            # fetch page
            url = item.item_steamPriceURL

            # headers required for response
            headers = {'Cookie': 'Steam_Language=english; birthtime=-2208959999;', 'User-Agent': 'Mozilla', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept': 'text/html', 'Accept-Encoding': 'gzip'}

            # fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
            # allow 30 seconds for response
            response = urlfetch.fetch(url, None, 'GET', headers, False, False, 30)

            # decompress
            f = StringIO.StringIO(response.content)
            c = gzip.GzipFile(fileobj=f)
            content = c.read()

            if response.status_code == 200:

                # parse metacritic page response - return score
                steamPrice = getSteamPrice(content)

                if (steamPrice != None):

                    logging.info('------ UPDATE STEAM PRICE v2 -------')
                    logging.info(item.item_name)
                    logging.info(steamPrice)

                    # upate item record
                    item.item_steamPrice = steamPrice
                    item.put()

    return HttpResponse('success', mimetype='text/plain', status='200')


# UPDATE STEAM PAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateSteamPage(request):

    deferred.defer(updateSteamPageDeferred)

    return HttpResponse('success', mimetype='text/plain', status='200')


# UPDATE STEAM PAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateSteamPageDeferred():
    # get items
    items = Items.query().fetch()

    # iterate items
    for item in items:

        # steam price URL not found
        if (item.item_steamPriceURL == None or item.item_steamPriceURL.strip() == ''):

            # search steam
            searchList = Steam.searchSteam(item.item_name)

            # add all names to array and item names to dictionary by name
            nameList = []
            searchDictionary = {}

            for steamItem in searchList:
                nameList.append(steamItem['name'])
                searchDictionary[steamItem['name']] = steamItem

            # get closest matches
            closestMatches = difflib.get_close_matches(item.item_name, nameList, 1)

            # match found
            if (len(closestMatches) != 0):
                firstMatch = closestMatches[0]

                logging.info('------ UPDATE STEAM PAGE v2 -------')
                logging.info(item.item_name)
                logging.info(searchDictionary[firstMatch]['page'])

                # update steam price info
                item.item_steamPriceURL = searchDictionary[firstMatch]['page']
                item.item_steamPrice = searchDictionary[firstMatch]['price']
                item.put()

    return HttpResponse('success', mimetype='text/plain', status='200')


# GET STEAM PRICE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getSteamPrice(response):

    # get response as etree
    html = etree.HTML(response)
    priceSel = CSSSelector('.game_purchase_price:first-child')

    # get price element
    priceElement = priceSel(html)

    try:
        # get score text
        steamPrice = priceElement[0].text.strip()

    except IndexError:
        steamPrice = None

    # return score
    return steamPrice


# UPDATE METACRITIC SCORE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateMetascore(request):

    # get items
    items = Items.query().fetch()

    # iterate items
    for item in items:

        # if metacriticPage is valid
        if (item.item_metacriticPage != None and item.item_metacriticPage != ''):

            # fetch page
            url = METACRITIC_BASE_URL + item.item_metacriticPage

            logging.info(url)

            # allow 30 seconds for response
            response = urlfetch.fetch(url, None, 'GET', {}, False, False, 30)

            if response.status_code == 200:

                # parse metacritic page response - return score
                metascore = getMetacriticScore(response.content)

                logging.info('------ METASCORE -------')
                logging.info('-------------------')
                logging.info(metascore)
                logging.info('-------------------')

                # upate item record
                item.item_metascore = metascore
                item.put()

    return HttpResponse('success', mimetype='text/plain', status='200')


# GET METACRITIC SCORE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getMetacriticScore(response):

    # get response as etree
    html = etree.HTML(response)
    scoreSel = CSSSelector('.metascore_summary .score_value')

    # get score element
    scoreElement = scoreSel(html)

    try:
        # get score text
        metascore = scoreElement[0].text.strip()

    except IndexError:
        metascore = '-1'

    # return score
    return metascore
