from google.appengine.api import urlfetch
from google.appengine.api import memcache

from django.http import HttpResponse

import urllib
import urllib2
import bottlenose

from lxml.cssselect import CSSSelector
from lxml import etree

import json
import logging

from tmz.keys import Keys

# amazon api properties
AMAZON_ACCESS_KEY = 'AMAZON_ACCESS_KEY'
AMAZON_SECRET_KEY = 'AMAZON_SECRET_KEY'
AMAZON_ASSOCIATE_TAG = 'codeco06-20'

# giantbomb api properties
GIANTBOMB_API_KEY = 'GIANTBOMB_API_KEY'



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SEARCH STEAM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def searchSteam(request):

    # http://store.steampowered.com/search/suggest?term=searchTerms&f=games

    if 'keywords' in request.GET:
        keywords = request.GET.get('keywords')

    # memcache key
    memcacheKey = 'steamTitle_' + keywords

    # return memcached search if available
    steamSearch = memcache.get(memcacheKey)

    if steamSearch is not None:
        logging.info('')
        logging.info('-------------- searchSteam CACHE HIT --------------')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')

        # return json
        return HttpResponse(json.dumps(steamSearch), mimetype='application/json')

    else:

        logging.info('')
        logging.info('-------------- searchSteam MISS --------------')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')

        url = 'http://store.steampowered.com/search/suggest?f=games&term=' + keywords
        response = urlfetch.fetch(url, None, 'GET', {}, False, False, 30)

        searchList = parseSteamSearch(response.content)

    return HttpResponse(json.dumps(searchList), mimetype='application/json')


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
# CACHE STEAM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def cacheSteam(request):

    if all(k in request.GET for k in ('keywords', 'url', 'price')):

        keywords = request.GET.get('keywords')
        url = request.GET.get('url')
        price = request.GET.get('price')

        # construct object to cache
        cachedObject = {
            'url': url,
            'price': price,
        }

        # memcache key
        memcacheKey = 'steamTitle_' + keywords

        # cache for 30 days
        if not memcache.add(memcacheKey, cachedObject, 2592000):
            logging.error('cacheSteam: Memcache set failed')
            logging.error(memcacheKey)
            return HttpResponse('FALSE', mimetype='text/html')

    return HttpResponse('TRUE', mimetype='text/html')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METACRITIC
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def searchMetacritic(request):

    if 'keywords' in request.GET:
        keywords = request.GET.get('keywords')

    if 'platform' in request.GET:
        platform = request.GET.get('platform')

    # memcache key
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
        return HttpResponse(json.dumps(metacriticSearch), mimetype='application/json')

    else:

        logging.info('')
        logging.info('-------------- searchMetacritic MISS --------------')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')

        url = 'http://www.metacritic.com/search/game/' + keywords + '/results'
        response = urlfetch.fetch(url, None, 'GET', {}, False, False, 30)

    # return raw response html
    return HttpResponse(response.content, mimetype='text/html')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# cacheMetacritic
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def cacheMetacritic(request):

    if 'keywords' in request.GET:
        keywords = request.GET.get('keywords')

    if 'platform' in request.GET:
        platform = request.GET.get('platform')

    if 'metascore' in request.GET:
        metascore = request.GET.get('metascore')

    if 'metascorePage' in request.GET:
        metascorePage = request.GET.get('metascorePage')

    # construct object to cache
    cachedObject = {'metascore': metascore, 'metascorePage': metascorePage}

    # memcache key
    memcacheKey = 'searchMetacritic_' + keywords + '_' + platform

    # cache for 7 days
    if not memcache.add(memcacheKey, cachedObject, 604800):
        logging.error('cacheMetacritic: Memcache set failed')
        logging.error(memcacheKey)
        return HttpResponse('FALSE', mimetype='text/html')

    return HttpResponse('TRUE', mimetype='text/html')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SEARCH GAMETRAILERS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def searchGametrailers(request):

    if 'keywords' in request.GET:
        keywords = request.GET.get('keywords')

    # memcache key
    memcacheKey = 'searchGametrailers_' + keywords

    # return memcached search if available
    gametrailersSearch = memcache.get(memcacheKey)

    if gametrailersSearch is not None:
        logging.info('')
        logging.info('-------------- searchGametrailers CACHE HIT --------------')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')

        # return json
        return HttpResponse(json.dumps(gametrailersSearch), mimetype='application/json')

    else:

        logging.info('')
        logging.info('-------------- searchGametrailers MISS --------------')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')

        url = 'http://www.gametrailers.com/search?keywords=' + keywords
        response = urlfetch.fetch(url, None, 'GET', {}, False, False, 30)

    # return raw response html
    return HttpResponse(response.content, mimetype='text/html')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CACHE GAMETRAILERS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def cacheGametrailers(request):

    if 'keywords' in request.GET:
        keywords = request.GET.get('keywords')

    if 'gametrailersPage' in request.GET:
        gametrailersPage = request.GET.get('gametrailersPage')

    # construct object to cache
    cachedObject = {'gametrailersPage': gametrailersPage}

    # memcache key
    memcacheKey = 'searchGametrailers_' + keywords

    # cache for 30 days
    if not memcache.add(memcacheKey, cachedObject, 2592000):
        logging.error('searchGametrailers: Memcache set failed')
        logging.error(memcacheKey)
        return HttpResponse('FALSE', mimetype='text/html')

    return HttpResponse('TRUE', mimetype='text/html')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AMAZON PRODUCT API REST PROXY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# searchAmazon
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def searchAmazon(request):

    amazon = bottlenose.Amazon(Keys.getKey(AMAZON_ACCESS_KEY), Keys.getKey(AMAZON_SECRET_KEY), AMAZON_ASSOCIATE_TAG)

    if 'keywords' in request.GET:
        keywords = request.GET.get('keywords')

    if 'browse_node' in request.GET:
        browseNode = request.GET.get('browse_node')

    if 'response_group' in request.GET:
        responseGroup = request.GET.get('response_group')

    if 'search_index' in request.GET:
        searchIndex = request.GET.get('search_index')

    if 'page' in request.GET:
        page = request.GET.get('page')

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
        return HttpResponse(search, mimetype='application/xml')

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

        return HttpResponse(response, mimetype='application/xml')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# detailAmazon
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def detailAmazon(request):

    # get request parameters
    if 'asin' in request.GET:
        asin = request.GET.get('asin')

    if 'response_group' in request.GET:
        responseGroup = request.GET.get('response_group')

    memcacheKey = 'detailAmazon_' + asin + '_' + responseGroup

    # return memcached detail if available
    detail = memcache.get(memcacheKey)

    if detail is not None:
        logging.info('')
        logging.info('-------------- detailAmazon HIT --------------')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')
        return HttpResponse(detail, mimetype='application/xml')

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

        return HttpResponse(response, mimetype='application/xml')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GIANT BOMB API REST PROXY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# searchGiantBomb
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def searchGiantBomb(request):

    queryParameters = {'resources': 'game', 'resource_type': 'game'}

    # field list
    if 'field_list' in request.GET:
        queryParameters['field_list'] = request.GET.get('field_list')

    if 'keywords' in request.GET:
        queryParameters['query'] = request.GET.get('keywords')

    if 'page' in request.GET:
        queryParameters['page'] = request.GET.get('page')

    response = giantBombAPICall('search', queryParameters)

    return HttpResponse(json.dumps(response), mimetype='application/json')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# detailGiantBomb
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def detailGiantBomb(request):

    queryParameters = {}

    # field list
    if 'field_list' in request.GET:
        queryParameters['field_list'] = request.GET.get('field_list')

    if 'id' in request.GET:
        id = request.GET.get('id')

        response = giantBombAPICall('game/' + id, queryParameters)

        return HttpResponse(json.dumps(response), mimetype='application/json')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# giantBombAPICall
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def giantBombAPICall(resource, queryParameters):

    parameters = urllib.urlencode(queryParameters)
    memcacheKey = 'giantBombAPICall_' + resource + '_' + parameters

    # return memcached detail if available
    giantbombData = memcache.get(memcacheKey)

    if giantbombData is not None:

        logging.info('')
        logging.info('-------------- giantBombAPICall HIT --------------')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')

        return giantbombData

    else:
        logging.info('')
        logging.info('-------------- giantBombAPICall MISS --------------')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')

        # http://api.giantbomb.com/search/?api_key=e89927b08203137d0252fbf1f611a38489edb208&format=xml&query=killzone
        api_string = 'http://api.giantbomb.com/' + resource + '/?api_key=' + Keys.getKey(GIANTBOMB_API_KEY) + '&format=json&' + urllib.urlencode(queryParameters)
        req = urllib2.Request(api_string, headers={'Accept-Encoding': 'gzip'})

        opener = urllib2.build_opener()
        f = opener.open(req)
        jsonResponse = json.load(f)

        # cache giantbomb detail for 1 day
        if not memcache.add(memcacheKey, jsonResponse, 86400):
            logging.error('detailGiantBomb: Memcache set failed')
            logging.error(memcacheKey)

        return jsonResponse
