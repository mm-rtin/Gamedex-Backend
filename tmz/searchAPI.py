from google.appengine.api import urlfetch
from google.appengine.api import memcache

from django.http import HttpResponse
from django.utils import simplejson

import urllib
import urllib2
import bottlenose

import logging

# amazon api properties
accessKey = '0JVZGYMSKN59DPNKRGR2'
secretKey = 'AImptXlEmeKcQREmkl6qCEomGnm7aoueigTOJlmL'
associate_tag = 'codeco06-20'
xml2JSON = 'http://xml2json-xslt.googlecode.com/svn/trunk/xml2json.xslt'

# giantbomb api properties
giantBombAPIKey = 'e89927b08203137d0252fbf1f611a38489edb208'


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METACRITIC
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def searchMetacritic(request):

    if 'keywords' in request.GET:
        keywords = request.GET.get('keywords')

    # memcache key
    memcacheKey = 'searchMetacritic_' + keywords

    # return memcached search if available
    metacriticSearch = memcache.get(memcacheKey)

    if metacriticSearch is not None:
        logging.info('')
        logging.info('************** searchMetacritic CACHE HIT **************')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')

        # return json
        return HttpResponse(simplejson.dumps(metacriticSearch), mimetype='application/json')

    else:

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

    if 'metascore' in request.GET:
        metascore = request.GET.get('metascore')

    if 'metascorePage' in request.GET:
        metascorePage = request.GET.get('metascorePage')

    # construct object to cache
    cachedObject = {'metascore': metascore, 'metascorePage': metascorePage}

    # memcache key
    memcacheKey = 'searchMetacritic_' + keywords

    # cache for 2 days
    if not memcache.add(memcacheKey, cachedObject, 127800):
        logging.error('searchMetacritic: Memcache set failed')
        return HttpResponse('FALSE', mimetype='text/html')

    return HttpResponse('TRUE', mimetype='text/html')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AMAZON PRODUCT API REST PROXY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# searchAmazon
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def searchAmazon(request):

    amazon = bottlenose.Amazon(accessKey, secretKey, associate_tag)

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
        logging.info('************** searchAmazon CACHE HIT **************')
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

        # cache amazon detail for 1 day
        if not memcache.add(memcacheKey, response, 86400):
            logging.error('searchAmazon: Memcache set failed')

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
        logging.info('************** detailAmazon HIT **************')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')
        return HttpResponse(detail, mimetype='application/xml')

    # get detail from source
    else:
        amazon = bottlenose.Amazon(accessKey, secretKey, associate_tag)
        response = amazon.ItemLookup(ItemId=asin, IdType='ASIN', ResponseGroup=responseGroup)

        # cache amazon detail for 1 day
        if not memcache.add(memcacheKey, response, 86400):
            logging.error('detailAmazon: Memcache set failed')

        return HttpResponse(response, mimetype='application/xml')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# cacheAmazonDetail
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def cacheAmazonDetail(request):

    if 'asin' in request.GET:
        asin = request.GET.get('asin')

    if 'response_group' in request.GET:
        responseGroup = request.GET.get('response_group')

    memcacheKey = 'detailAmazon_' + asin + '_' + responseGroup

    # construct object to cache
    cachedObject = {'metascore': metascore, 'metascorePage': metascorePage}

    # memcache key
    memcacheKey = 'searchMetacritic_' + keywords

    # cache for 2 days
    if not memcache.add(memcacheKey, cachedObject, 127800):
        logging.error('searchMetacritic: Memcache set failed')
        return HttpResponse('FALSE', mimetype='text/html')

    return HttpResponse('TRUE', mimetype='text/html')


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

    return HttpResponse(simplejson.dumps(response), mimetype='application/json')


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

    return HttpResponse(simplejson.dumps(response), mimetype='application/json')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# giantBombAPICall
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def giantBombAPICall(resource, queryParameters):

    # http://api.giantbomb.com/search/?api_key=e89927b08203137d0252fbf1f611a38489edb208&format=xml&query=killzone
    api_string = 'http://api.giantbomb.com/' + resource + '/?api_key=' + giantBombAPIKey + '&format=json&' + urllib.urlencode(queryParameters)
    req = urllib2.Request(api_string, headers={'Accept-Encoding': 'gzip'})

    opener = urllib2.build_opener()
    f = opener.open(req)
    jsonResponse = simplejson.load(f)

    return jsonResponse
