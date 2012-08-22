from google.appengine.api import urlfetch

from django.http import HttpResponse

from lxml.cssselect import CSSSelector
from lxml import etree

import logging

import StringIO
import gzip
import json

import searchAPI


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# getSteamGames
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getSteamGames(request):

    if 'id' in request.GET:

        url = 'http://steamcommunity.com/id/%s/games?tab=all' % (request.GET.get('id'))

        headers = {'Accept-Encoding': 'gzip'}

        # fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
        # allow 30 seconds for response
        response = urlfetch.fetch(url, None, 'GET', headers, False, False, 30)

        # decompress
        f = StringIO.StringIO(response.content)
        c = gzip.GzipFile(fileobj=f)
        content = c.read()

        if response.status_code == 200:
            return HttpResponse(content, mimetype='text/html')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# getPSNGames_endpoint
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getPSNGames_endpoint(request):

    getPSNGames(request.GET.get('id'))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# getPSNGames
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getPSNGames(id):

    # GET /playstation/psn/profile/Michu/get_ordered_trophies_data HTTP/1.1
    # Host    us.playstation.com
    # X-Requested-With    XMLHttpRequest
    # User-Agent  Mozilla
    # Accept  text/html
    # Accept-Encoding gzip,deflate,sdch
    # Accept-Charset    ISO-8859-1,utf-8;q=0.7,*;q=0.3

    # playstation user games/trophy url
    url = 'http://us.playstation.com/playstation/psn/profile/%s/get_ordered_trophies_data' % (id)

    # headers required for response
    headers = {'Host': 'us.playstation.com', 'X-Requested-With': 'XMLHttpRequest', 'User-Agent': 'Mozilla', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept': 'text/html', 'Accept-Encoding': 'gzip'}

    # fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
    # allow 30 seconds for response
    response = urlfetch.fetch(url, None, 'GET', headers, False, False, 30)

    # decompress
    f = StringIO.StringIO(response.content)
    c = gzip.GzipFile(fileobj=f)
    content = c.read()

    # valid response - begin parse
    if response.status_code == 200:

        # game titles imported
        importedTitles = []

        # iterate game list
        html = etree.HTML(content)

        titleSectionSel = CSSSelector('.titlesection')
        titleSel = CSSSelector('.gameTitleSortField')

        # for each game > get title
        for row in titleSectionSel(html):

            try:
                titleElement = titleSel(row)

                # get game title as plain ascii and remove non-ascii characters
                gameTitle = titleElement[0].text.encode('ascii', 'ignore').strip()

                # add title
                importedTitles.append(gameTitle)

            except IndexError:
                logging.error('PSN Import: IndexError')

        return importedTitles


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# getXBLGames
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getXBLGames(request):

    if 'id' in request.GET:

        # xboxapi url
        url = 'https://xboxapi.com/games/%s' % (request.GET.get('id'))

        headers = {}

        # fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
        # allow 30 seconds for response
        response = urlfetch.fetch(url, None, 'GET', headers, False, False, 30, True)

        if response.status_code == 200:
            return HttpResponse(response.content, mimetype='application/json')
