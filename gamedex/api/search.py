"""search.py: API for accessing Search Sources """

__author__ = "Michael Martin"
__status__ = "Production"

import StringIO
import gzip
import json
import logging
import urllib


from google.appengine.api import urlfetch
from google.appengine.api import memcache

from django.http import HttpResponse

from management.keys import Keys
from services.searchSources import Steam, Amazon, Metacritic

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

        # get steam results
        searchList = Steam.searchSteam(keywords)

        return HttpResponse(json.dumps(searchList), mimetype='application/json')

    else:
        return HttpResponse('missing_param', mimetype='text/plain', status='500')


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
        if memcache.add(memcacheKey, cachedObject, 2592000):
            return HttpResponse('TRUE', mimetype='text/html')

        else:
            logging.error('cacheSteam: Memcache set failed')
            logging.error(memcacheKey)
            return HttpResponse('FALSE', mimetype='text/html')

    else:
        return HttpResponse('missing_param', mimetype='text/plain', status='500')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METACRITIC
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def searchMetacritic(request):

    platform = ''

    if 'keywords' in request.GET:
        keywords = request.GET.get('keywords')

    if 'platform' in request.GET:
        platform = request.GET.get('platform')

    # search metacritic
    (response, isJSON) = Metacritic.searchMetacritic(keywords, platform)

    if (isJSON):
        # return json
        return HttpResponse(json.dumps(response), mimetype='application/json')
    else:
        # return raw response html
        return HttpResponse(response, mimetype='text/html')


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

    if all(k in request.GET for k in ('keywords', 'browse_node', 'response_group', 'search_index', 'page')):

        # get request parameters
        keywords = request.GET.get('keywords')
        browseNode = request.GET.get('browse_node')
        responseGroup = request.GET.get('response_group')
        searchIndex = request.GET.get('search_index')
        page = request.GET.get('page')

        # search amazon
        response = Amazon.searchAmazon(keywords, browseNode, responseGroup, searchIndex, page)

        return HttpResponse(response, mimetype='application/xml')
    else:
        return HttpResponse('missing_param', mimetype='text/plain', status='500')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# detailAmazon
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def detailAmazon(request):

    if all(k in request.GET for k in ('asin', 'response_group')):

        # get request parameters
        asin = request.GET.get('asin')
        responseGroup = request.GET.get('response_group')

        # get amazon detail response
        response = Amazon.detailAmazon(asin, responseGroup)

        return HttpResponse(response, mimetype='application/xml')

    else:
        return HttpResponse('missing_param', mimetype='text/plain', status='500')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GIANT BOMB API REST PROXY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~z
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

    if response:
        return HttpResponse(response, mimetype='application/json')
    else:
        return HttpResponse('error', mimetype='text/plain', status='500')


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

        response = giantBombAPICall('game/3030-' + id, queryParameters)

        if response:
            return HttpResponse(response, mimetype='application/json')
        else:
            return HttpResponse('error', mimetype='text/plain', status='500')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# videoGiantBomb
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def videoGiantBomb(request):

    queryParameters = {}

    # field list
    if 'field_list' in request.GET:
        queryParameters['field_list'] = request.GET.get('field_list')

    if 'id' in request.GET:
        id = request.GET.get('id')

        response = giantBombAPICall('video/2300-' + id, queryParameters)

        if response:
            return HttpResponse(response, mimetype='application/json')
        else:
            return HttpResponse('error', mimetype='text/plain', status='500')


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

        # http://api.giantbomb.com/search/?api_key=xxxxxxxxxxxxxxxxxxx&format=xml&query=killzone
        api_string = 'http://www.giantbomb.com/api/' + resource + '/?api_key=' + Keys.getKey(GIANTBOMB_API_KEY) + '&format=json&' + urllib.urlencode(queryParameters)

        # fetch - accept gzip (url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
        headers = {'Accept-Encoding': 'gzip'}
        response = urlfetch.fetch(api_string, None, 'GET', headers, False, False, 30)

        # decompress
        f = StringIO.StringIO(response.content)
        c = gzip.GzipFile(fileobj=f)
        content = c.read()

        if response.status_code == 200:

            # cache giantbomb detail for 1 day
            if not memcache.add(memcacheKey, content, 86400):
                logging.error('detailGiantBomb: Memcache set failed')
                logging.error(memcacheKey)

            return content

        else:
            return False
