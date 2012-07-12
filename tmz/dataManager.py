from google.appengine.api import urlfetch
from django.http import HttpResponse

from lxml.cssselect import CSSSelector
from lxml import etree

import logging

# database models
from tmz.models import Items

# constants
METACRITIC_BASE_URL = 'http://www.metacritic.com'


# UPDATE METACRITIC SCORE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateMetascore(request):

    # get items
    items = Items.objects.all()

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
                item.save()

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
