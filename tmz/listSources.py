from google.appengine.api import urlfetch
from google.appengine.api import memcache

from django.http import HttpResponse
from django.utils import simplejson

from lxml.cssselect import CSSSelector
from lxml import etree

from boto.s3.connection import S3Connection

import logging

# constants
# base url
S3_URL = 'https://s3.amazonaws.com/'
# site bucket
UPCOMING_LIST_BUCKET = 's3.t-minuszero.com-upcominglist'

# S3 Properties
AWS_HEADERS = {
    'Cache-Control': 'max-age=86400,public'
}
AWS_ACL = 'public-read'


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GAMESTATS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def gameStatsListByGPM(request):

    if 'platform' in request.GET:
        platform = request.GET.get('platform')

    # return memcached list if available
    gameStatsByGPM = memcache.get('gameStatsListByGPM_' + platform)
    if gameStatsByGPM is not None:
        return HttpResponse(simplejson.dumps(gameStatsByGPM), mimetype='application/json')

    # load list from source
    else:

        # http://www.gamestats.com/index/gpm/xbox-360.html
        url = 'http://www.gamestats.com/index/gpm/' + platform + '.html'

        # fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
        # allow 15 seconds for response
        response = urlfetch.fetch(url, None, 'GET', {}, False, False, 15)

        if response.status_code == 200:

            # parse game stats list result
            gameStatsList = parseGameStatsListByGPM(response.content)

            # cache game stats list for 1 day
            if not memcache.add('gameStatsListByGPM_' + platform, gameStatsList, 86400):
                logging.error('gameStatsListByGPM: Memcache set failed')

            return HttpResponse(simplejson.dumps(gameStatsList), mimetype='application/json')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PARSE GAME STATS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def parseGameStatsListByGPM(response):

    list = []

    try:
        html = etree.HTML(response)

        # select all tr from 3rd table
        rowSel = CSSSelector('table:nth-child(3) tr')
        # select all 2nd tds
        tdSel = CSSSelector('td:nth-child(2) a')

        for row in rowSel(html):

            try:
                # get 2nd td elements from row
                element = tdSel(row)

                name = element[0].text.strip()
                url = element[0].get('href')

                if (name != 'Next 50'):
                    listObj = {'name': name, 'gameStatsPage': url}
                    list.append(listObj)

            except IndexError:
                print('parseGameStatsListByGPM: IndexError')

    except:
        print('parseGameStatsListByGPM: Parse Error')

    # return list
    return list


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IGN
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ignUpcomingList(request):

    if 'platform' in request.GET:
        platform = request.GET.get('platform')

    # return memcached list if available
    result = memcache.get('ignUpcomingList_' + platform)
    if result is not None:
        return HttpResponse(simplejson.dumps(result), mimetype='application/json')

    # load list from source
    else:

        # http://pc.ign.com/index/upcoming.html
        url = 'http://' + platform + '.ign.com/index/upcoming.html'

        # fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
        # allow 15 seconds for response
        response = urlfetch.fetch(url, None, 'GET', {}, False, False, 15)

        if response.status_code == 200:

            # parse game stats list result
            result = parseIGNUpcomingList(response.content)

            # cache game stats list for 1 day
            if not memcache.add('ignUpcomingList_' + platform, result, 86400):
                logging.error('ignUpcomingList: Memcache set failed')

            return HttpResponse(simplejson.dumps(result), mimetype='application/json')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PARSE IGN UPCOMING LIST
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def parseIGNUpcomingList(response):

    list = []

    # s3 connection
    s3conn = S3Connection('0JVZGYMSKN59DPNKRGR2', 'AImptXlEmeKcQREmkl6qCEomGnm7aoueigTOJlmL', is_secure=False)

    html = etree.HTML(response)

    tableSel = CSSSelector('#table-section-index .game-row')
    nameSel = CSSSelector('.title-game a')
    imageSel = CSSSelector('.box-art img')
    dateSel = CSSSelector('td:nth-child(3)')

    for row in tableSel(html):

        try:
            nameElement = nameSel(row)
            imageElement = imageSel(row)
            dateElement = dateSel(row)

            name = nameElement[0].text.strip()
            url = nameElement[0].get('href').strip()
            image = imageElement[0].get('src').strip()
            date = dateElement[0].text.strip()

            # copy IGN image to S3 bucket
            image = copyImageToS3(image, s3conn)

            logging.error(image)

            listObj = {'name': name, 'IGNPage': url, 'calendarDate': date, 'mediumImage': image}
            list.append(listObj)

        except IndexError:
            logging.error('parseIGNUpcomingList: IndexError')

    # return list
    return list


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# COPY LIST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def copyImageToS3(url, s3conn):

    # get s3 bucket
    bucket = s3conn.get_bucket(UPCOMING_LIST_BUCKET, validate=False)

    # get filename and extension
    fileName = url.split('/')[-1]
    extension = fileName.split('.')[-1]

    # load url
    response = urlfetch.fetch(url, None, 'GET', {}, False, False, 15)

    # create new S3 key, set mimetype and Expires header
    k = bucket.new_key(fileName)
    k.content_type = 'image/' + extension

    # write file from response string set public read permission
    k.set_contents_from_string(response.content, headers=AWS_HEADERS, replace=False, policy=AWS_ACL)
    k.set_acl('public-read')

    # s3 url
    return S3_URL + UPCOMING_LIST_BUCKET + '/' + fileName
