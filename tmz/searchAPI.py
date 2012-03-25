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
def itemSearchMetacritic(request):

    if 'keywords' in request.GET:
        keywords = request.GET.get('keywords')

    # memcache key
    memcacheKey = 'itemSearchMetacritic_' + keywords

    # return memcached search if available
    metacriticSearch = memcache.get(memcacheKey)

    if metacriticSearch is not None:
        logging.info('')
        logging.info('************** itemSearchMetacritic CACHE HIT **************')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')

        return HttpResponse(metacriticSearch, mimetype='text/html')

    else:

        # http://www.metacritic.com/search/game/something/results
        url = 'http://www.metacritic.com/search/game/' + keywords + '/results'
        response = urlfetch.fetch(url, None, 'GET', {}, False, False, 15)

        # cache for 2 days
        if not memcache.add(memcacheKey, response.content, 127800):
            logging.error('itemSearchMetacritic: Memcache set failed')

    return HttpResponse(response.content, mimetype='text/html')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AMAZON PRODUCT API REST PROXY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# item search
def itemSearchAmazon(request):

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
    memcacheKey = 'itemSearchAmazon_' + keywords + '_' + browseNode + '_' + responseGroup + '_' + searchIndex + '_' + page

    # return memcached search if available
    itemSearch = memcache.get(memcacheKey)

    if itemSearch is not None:
        logging.info('')
        logging.info('************** itemSearchAmazon CACHE HIT **************')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')
        return HttpResponse(itemSearch, mimetype='application/xml')

    else:
        # Availability='Available', Condition='All', MerchantId='Amazon', MinimumPrice='800', MaximumPrice='13500'
        if browseNode == '0':
            response = amazon.ItemSearch(SearchIndex=searchIndex, Title=keywords, ResponseGroup=responseGroup, ItemPage=page, Sort='salesrank')
        else:
            response = amazon.ItemSearch(SearchIndex=searchIndex, Title=keywords, ResponseGroup=responseGroup, ItemPage=page, Sort='salesrank', MinimumPrice='800', MaximumPrice='13500', BrowseNode=browseNode)

        # cache amazon detail for 1 day
        if not memcache.add(memcacheKey, response, 86400):
            logging.error('itemSearchAmazon: Memcache set failed')

        return HttpResponse(response, mimetype='application/xml')


# item detail by asin
def itemDetailAmazon(request):

    # get request parameters
    if 'asin' in request.GET:
        asin = request.GET.get('asin')

    if 'response_group' in request.GET:
        responseGroup = request.GET.get('response_group')

    memcacheKey = 'itemDetailAmazon_' + asin + '_' + responseGroup

    # return memcached detail if available
    itemDetail = memcache.get(memcacheKey)

    if itemDetail is not None:
        logging.info('')
        logging.info('************** itemDetailAmazon HIT **************')
        logging.info(memcacheKey)
        logging.info('')
        logging.info('')
        return HttpResponse(itemDetail, mimetype='application/xml')

    # get detail from source
    else:
        amazon = bottlenose.Amazon(accessKey, secretKey, associate_tag)
        response = amazon.ItemLookup(ItemId=asin, IdType='ASIN', ResponseGroup=responseGroup)

        # cache amazon detail for 1 day
        if not memcache.add(memcacheKey, response, 86400):
            logging.error('itemDetailAmazon: Memcache set failed')

        return HttpResponse(response, mimetype='application/xml')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GIANT BOMB API REST PROXY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# item search
def itemSearchGiantBomb(request):

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


# item detail by gbombID
def itemDetailGiantBomb(request):

    queryParameters = {}

    # field list
    if 'field_list' in request.GET:
        queryParameters['field_list'] = request.GET.get('field_list')

    if 'id' in request.GET:
        id = request.GET.get('id')

    response = giantBombAPICall('game/' + id, queryParameters)

    return HttpResponse(simplejson.dumps(response), mimetype='application/json')


# giantBombAPICall
def giantBombAPICall(resource, queryParameters):

    # http://api.giantbomb.com/search/?api_key=e89927b08203137d0252fbf1f611a38489edb208&format=xml&query=killzone
    api_string = 'http://api.giantbomb.com/' + resource + '/?api_key=' + giantBombAPIKey + '&format=json&' + urllib.urlencode(queryParameters)
    req = urllib2.Request(api_string, headers={'Accept-Encoding': 'gzip'})

    opener = urllib2.build_opener()
    f = opener.open(req)
    jsonResponse = simplejson.load(f)

    return jsonResponse
