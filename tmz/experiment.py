from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from django.core import serializers

import logging
import json

# database models
from tmz.models import Users, Items, Tags, ItemTagUser


# GET DIRECTORY OF ID/3RD PARTY IDs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getDirectory(request):

    try:
        user = Users.objects.get(pk='69a92fe7-5fc1-4607-9e5e-04ce1a7e725b', user_secret_key='1')
    except Users.DoesNotExist:
        user = None

    # validate secretKey against user
    if user:

        # get tag items
        try:
            itemTagUsers = ItemTagUser.objects.filter(user=user)
        except ItemTagUser.DoesNotExist:
            itemTagUsers = None

    data = serializers.serialize("json", itemTagUsers)

    return HttpResponse(data, mimetype='application/json')

# GET DIRECTORY OF ID/3RD PARTY IDs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getDirectory2(request):

    try:
        user = Users.objects.get(pk='1', user_secret_key='1')
    except Users.DoesNotExist:
        user = None

    # validate secretKey against user
    if user:

        # get tag items
        try:
            itemTagUsers = ItemTagUser.objects.select_related('item__item_asin', 'item__item_gbombID').filter(user=user)
        except ItemTagUser.DoesNotExist:
            itemTagUsers = None

        directoryItems = {}

        # list items found
        if itemTagUsers:

            # construct python dictionary
            for items in itemTagUsers:

                directoryItems[items.item.pk] = {
                    'aid': items.item.item_asin,
                    'gid': items.item.item_gbombID,
                }

    return HttpResponse(json.dumps({'directory': directoryItems}), mimetype='application/json')
