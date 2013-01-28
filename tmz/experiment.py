from google.appengine.ext import ndb

from django.http import HttpResponse
from django.core import serializers

import logging
import json

# database models
from tmz.models import Users, Items, Tags, ItemTagUser


# GET DIRECTORY OF ID/3RD PARTY IDs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getDirectory(request):

    user = Users.query(Users.user_email == 'demo@gamedex.net').get()

    if user:

        # get tag items
        itemTagUsers = ItemTagUser.query(ItemTagUser.user == user.key).fetch(projection=['item', 'tag', 'item_gameStatus', 'item_playStatus', 'item_userRating'])

        itemTagUserDict = {}
        directoryItems = {}
        itemKeyList = []

        # list items found
        if itemTagUsers:

            # add item keys to list
            for itemTagUser in itemTagUsers:

                # append key to list
                itemKeyList.append(itemTagUser.item)

                # add itemTagUser info to dictionary
                itemTagUserDict[itemTagUser.item.urlsafe()] = {'key': itemTagUser.key.urlsafe(), 'tag': itemTagUser.tag.urlsafe(), 'item_gameStatus': itemTagUser.item_gameStatus, 'item_playStatus': itemTagUser.item_playStatus, 'item_userRating': itemTagUser.item_userRating}

            # get batch of items
            items = ndb.get_multi(itemKeyList)

            # iterate item batch
            for item in items:

                itemKey = item.key.urlsafe()

                # create item object
                if itemKey not in directoryItems:

                    directoryItems[itemKey] = {
                        'aid': item.item_asin,
                        'gid': item.item_gbombID,
                        'gs': itemTagUserDict[itemKey]['item_gameStatus'],
                        'ps': itemTagUserDict[itemKey]['item_playStatus'],
                        'ur': itemTagUserDict[itemKey]['item_userRating'],
                        't': {},
                        'tc': 0
                    }

                # append tag
                directoryItems[itemKey]['t'][itemTagUserDict[itemKey]['tag']] = itemTagUserDict[itemKey]['key']
                directoryItems[itemKey]['tc'] = directoryItems[itemKey]['tc'] + 1

        # serialize and return directory
        return HttpResponse(json.dumps({'directory': directoryItems}), mimetype='application/json')
