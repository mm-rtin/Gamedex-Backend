"""gameSources.py: Import Games from third party sources: Steam, PSN and XBL """

__author__ = "Michael Martin"
__status__ = "Production"

import StringIO
import gzip
import json
import urllib
import logging

from google.appengine.api import urlfetch

from lxml.cssselect import CSSSelector
from lxml import etree


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# getSteamGames
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getSteamGames(id):

    url = 'http://steamcommunity.com/id/%s/games?tab=all' % id

    headers = {'Accept-Encoding': 'gzip'}

    # fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
    # allow 30 seconds for response
    response = urlfetch.fetch(url, None, 'GET', headers, False, False, 30)

    # decompress
    f = StringIO.StringIO(response.content)
    c = gzip.GzipFile(fileobj=f)
    content = c.read()

    if response.status_code == 200:

        html = etree.HTML(content)
        scriptSel = CSSSelector('script')

        gamesScript = ''

        # iterate all script tags and find rgGames in script
        for row in scriptSel(html):
            if (row.text is not None and 'rgGames' in row.text):
                gamesScript = row.text

        # parse json in gamesScript
        jsonString = gamesScript[gamesScript.find('['):gamesScript.find(']') + 1]
        jsonObj = json.loads(jsonString)

        # clean json
        gameList = []
        for game in jsonObj:
            gameList.append(game['name'])

        return gameList

    return None


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# getPSNGames
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getPSNGames(id):

     # playstation user games/trophy url
    url = 'http://us.playstation.com/playstation/psn/profile/' + id + '/get_ordered_trophies_data'

    # headers required for response
    headers = {
        'Host': 'us.playstation.com',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept': 'text/html',
        'Accept-Encoding': 'gzip',
        'Cookie': 'SONYCOOKIE1=677685440.20480.0000; __unam=756c574-13f21832b06-3a7fa02-1; s_cc=true; s_sq=%5B%5BB%5D%5D; s_vi=[CS]v1|28D68036851D1C3F-6000012C40010A16[CE]; TICKET=MQAAAAAAAPgwAACsAAgAFADR5abPxLs4rBysKuLG8KfkyEcbAAEABAAAAQAABwAIAAABP0oPi1AA%0ABwAIAAABP0815uAAAgAIfd4skexVS6sABAAgTWljaHUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA%0AAAAACAAEdXMAAQAEAARhNgAAAAgAGFVQOTAwMi1OUFdBMDAwMzVfMDAAAAAAADARAAQHvwEcAAEA%0ABB4AAgAwEAAAAAAAADACAEQACAAE2%2B8LsgAIADgwNgIZAJVhqTJ9ZKQ2ornliP9bM6Q3s7AvBL1o%0AxwIZAI7HkjNkzHGNFFGrroEXi1qaHTJf5FTR%2FA%3D%3D; PSNS2STICKET=MQAAAAAAAPgwAACsAAgAFDDDhl72dxY1vp7Q5cvzD1LSy8JlAAEABAAAAQAABwAIAAABP0oPi7UA%0ABwAIAAABP0815uAAAgAIfd4skexVS6sABAAgTWljaHUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA%0AAAAACAAEdXMAAQAEAARhNgAAAAgAGElWMDAwMS1OUFhTMDEwMDRfMDAAAAAAADARAAQHvwEcAAEA%0ABB4AAgAwEAAAAAAAADACAEQACAAEyS7rGwAIADgwNgIZAK1aVaE866zmIoUlf3U3rIxlD8pq5g08%0ApwIZAKrRjrnMhwDSW%2FGzMoaEHP9cez1SQb%2Bh4Q%3D%3D;'
    }

    # fetch url - send form data, allow 30 seconds for response
    response = urlfetch.fetch(url=url, method=urlfetch.GET, headers=headers, deadline=30)

    # valid response - begin parse
    if response.status_code == 200:

        # decompress
        f = StringIO.StringIO(response.content)
        c = gzip.GzipFile(fileobj=f)
        content = c.read()

        # game titles imported
        importedTitles = []

        # iterate game list
        html = etree.HTML(content)

        titleSectionSel = CSSSelector('.recentitems')
        titleSel = CSSSelector('.gametitle a')

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

    return None


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# getXBLGames
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getXBLGames(id):

    # convert spaces to +
    id = id.replace(' ', '+')

    # url
    url = 'http://www.xboxgamertag.com/search/%s' % (id)

    headers = {'Accept-Encoding': 'gzip'}

    # fetch(url, payload=None, method=GET, headers={}, allow_truncated=False, follow_redirects=True, deadline=None, validate_certificate=None)
    # allow 30 seconds for response
    response = urlfetch.fetch(url, None, 'GET', headers, False, False, 30, True)

    # decompress
    f = StringIO.StringIO(response.content)
    c = gzip.GzipFile(fileobj=f)
    content = c.read()

    logging.info(content)

    # valid response - begin parse
    if response.status_code == 200:

        # game titles imported
        importedTitles = []

        # iterate game list
        html = etree.HTML(content)

        titleSectionSel = CSSSelector('#recentGamesTable tr')
        titleSel = CSSSelector('.gameName a')

        # for each game > get title
        for row in titleSectionSel(html):

            try:
                titleElement = titleSel(row)

                # get game title as plain ascii and remove non-ascii characters
                gameTitle = titleElement[0].text.encode('ascii', 'ignore').strip()

                # add title
                importedTitles.append(gameTitle)

            except IndexError:
                logging.error('XBL Import: IndexError')

        return importedTitles

    return None
