from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import simplejson

import hashlib
import time
import uuid

# database models
from tmz.models import Users, Items, Tags, ItemTagUser


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# T_MINUS ZERO REST API
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# USER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# LOGIN
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def login(request):

    if (request.POST):

        if 'user_email' in request.POST and 'user_password' in request.POST:

            # get user parameters
            userEmail = request.POST.get('user_email')
            userPassword = request.POST.get('user_password')

            # hash password
            userPassword = hashlib.md5(userPassword).hexdigest()

            # validate login
            try:
                user = Users.objects.get(user_email=userEmail, user_password=userPassword)
            except Users.DoesNotExist:
                user = None

            if user:

                # generate secret key
                secretKey = hashlib.md5(userEmail)
                secretKey.update(str(time.time()))
                secretKey = secretKey.hexdigest()

                # save secret key
                user.user_secret_key = secretKey
                user.save()

                # construct json return object
                data = {'userID': user.pk, 'secretKey': secretKey}

                return HttpResponse(simplejson.dumps(data), mimetype='application/json')
            else:
                return HttpResponse('false', mimetype='text/html')

        else:
            return HttpResponse('false', mimetype='text/html')

    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# CREATE USER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def createUser(request):

    if (request.POST):

        # collect user parameters
        userEmail = request.POST.get('user_email')
        userPassword = request.POST.get('user_password')

        # check existing email
        try:
            user = Users.objects.get(user_email=userEmail)
        except Users.DoesNotExist:
            user = None

        # user does not exist: create new user
        if user == None:
            # hash password
            userPassword = hashlib.md5(userPassword).hexdigest()

            # create user
            guid = str(uuid.uuid4())
            user = Users(id=guid, user_email=userEmail, user_password=userPassword, user_secret_key='')
            user.save()

            # generate secret key
            secretKey = hashlib.md5(userEmail)
            secretKey.update(str(time.time()))
            secretKey = secretKey.hexdigest()

            # save secret key
            user.user_secret_key = secretKey
            user.save()

            # create default list
            listguid = str(uuid.uuid4())
            newList = Tags(id=listguid, user=user, list_name='wishlist')
            newList.save()

            # construct json return object
            data = {'userID': user.pk, 'secretKey': secretKey}

            return HttpResponse(simplejson.dumps(data), mimetype='application/json')

        # user exists
        else:
            return HttpResponse(simplejson.dumps({'status': 'user_exists'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# READ USER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# UPDATE USER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# DELETE USER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TAGS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# CREATE TAG
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def createList(request):

    if (request.POST):

        # collect list item parameters
        userID = request.POST.get('user_id')
        secretKey = request.POST.get('uk')
        listName = request.POST.get('list_name').strip()

        # get user by userid
        try:
            user = Users.objects.get(pk=userID)
        except Users.DoesNotExist:
            user = None

        # validate secretKey against user
        if user and user.user_secret_key == secretKey:

            # create list
            guid = str(uuid.uuid4())
            newList = Tags(id=guid, user=user, list_name=listName)

            # prevent demo account from saving data
            if (secretKey != '1'):
                newList.save()

            returnData = {'listID': newList.pk, 'listName': listName}

            return HttpResponse(simplejson.dumps(returnData), mimetype='application/json')

        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# READ TAGS
# return a list of tags
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def getList(request):

    if (request.POST):

        # collect list item parameters
        userID = request.POST.get('user_id').strip()
        secretKey = request.POST.get('uk').strip()

        # get user by userid
        try:
            user = Users.objects.get(pk=userID)
        except Users.DoesNotExist:
            user = None

        # validate secretKey against user
        if user and user.user_secret_key == secretKey:

            listDictionary = {'list': []}

            # get lists
            try:
                lists = Tags.objects.filter(user=user)
            except Tags.DoesNotExist:
                lists = None

            # lists found
            if lists:

                usersList = []
                # construct python dictionary
                for item in lists:
                    usersList.append({'listID': item.pk, 'listName': item.list_name})

                listDictionary = {'list': usersList}

                # serialize and return lists
                return HttpResponse(simplejson.dumps(listDictionary), mimetype='application/json')

            else:
                return HttpResponse(simplejson.dumps(listDictionary), mimetype='application/json')
        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# UPDATE TAG
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# DELETE TAG
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def deleteList(request):

    if (request.POST):

        # collect item parameters
        userID = request.POST.get('user_id').strip()
        secretKey = request.POST.get('uk').strip()

        tagID = request.POST.get('id').strip()

        # prevent demo account
        if (secretKey == '1'):
            return HttpResponse(simplejson.dumps({'status': 'demo'}), mimetype='application/json')

        # get user by userid
        try:
            existingUser = Users.objects.get(pk=userID, user_secret_key=secretKey)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser:

            # get all ItemTagUser entries in List
            try:
                itemTagUser = ItemTagUser.objects.filter(tag=tagID, user=existingUser)
            except ItemTagUser.DoesNotExist:
                itemTagUser = None

            # get tag entry
            try:
                tag = Tags.objects.get(pk=tagID, user=existingUser)
            except Tags.DoesNotExist:
                tag = None

            # found record(s) > delete ItemTagUser entries
            if itemTagUser:
                itemTagUser.delete()

            if tag:
                tag.delete()
                return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')

            return HttpResponse(simplejson.dumps({'status': 'record not found'}), mimetype='application/json')

        else:
            return HttpResponse(simplejson.dumps({'status': 'user not found'}), mimetype='application/json')

    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ITEMS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# CREATE ITEM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def createListItem(request):

    if (request.POST):

        # collect list item parameters
        initialProvider = request.POST.get('ip')
        asin = request.POST.get('aid')
        gbombID = request.POST.get('gid')

        itemName = request.POST.get('n')
        releaseDate = request.POST.get('rd')
        platform = request.POST.get('p')
        smallImage = request.POST.get('si')
        thumbnailImage = request.POST.get('ti')
        largeImage = request.POST.get('li')

        metacriticPage = request.POST.get('mp')
        metascore = request.POST.get('ms')

        gameStatus = request.POST.get('gs')
        playStatus = request.POST.get('ps')
        userRating = request.POST.get('ur')

        # get tagIDs as array
        tagIDs = request.POST.getlist('lids[]')

        # authentication
        userID = request.POST.get('uid')
        secretKey = request.POST.get('uk')

        # get user by userid
        try:
            existingUser = Users.objects.get(pk=userID)
        except Users.DoesNotExist:
            existingUser = None

        # get existing item
        try:
            existingItem = None
            if asin != '0':
                existingItem = Items.objects.get(item_asin=asin, user=existingUser)
            elif gbombID != '0':
                existingItem = Items.objects.get(item_gbombID=gbombID, user=existingUser)

        except Items.DoesNotExist:
            existingItem = None

        # validate secretKey against user
        if existingUser and existingUser.user_secret_key == secretKey:

            # create new item
            if (existingItem is None):
                guid = str(uuid.uuid4())
                item = Items(
                    id=guid,
                    user=existingUser,
                    item_initialProvider=initialProvider,
                    item_asin=asin,
                    item_gbombID=gbombID,
                    item_name=itemName,
                    item_releasedate=releaseDate,
                    item_platform=platform,
                    item_smallImage=smallImage,
                    item_thumbnailImage=thumbnailImage,
                    item_largeImage=largeImage,
                    item_metacriticPage=metacriticPage,
                    item_metascore=metascore,
                    item_gameStatus=gameStatus,
                    item_playStatus=playStatus,
                    item_userRating=userRating
                )

                # prevent demo account from saving data
                if (secretKey != '1'):
                    item.save()

            # item already exists, use instead
            else:
                item = existingItem

            # create link between Item, Tag and User for multiple tags
            tagIDsAdded = []
            idsAdded = []

            for tagID in tagIDs:
                guid = str(uuid.uuid4())

                # prevent demo account from saving data
                if (secretKey != '1'):
                    # get tag
                    tag = Tags.objects.get(pk=tagID)
                    # create link
                    link = ItemTagUser(id=guid, user=existingUser, tag=tag, item=item)
                    link.save()

                # record item ids and tag ids that have been added
                tagIDsAdded.append(tagID)
                idsAdded.append(guid)

            returnData = {'idsAdded': idsAdded, 'itemID': item.pk, 'tagIDsAdded': tagIDsAdded}

            return HttpResponse(simplejson.dumps(returnData), mimetype='application/json')

        else:
            return HttpResponse('FALSE', mimetype='text/html')

    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# UPDATE ITEM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def updateItem(request):

    if (request.POST):

        # collect list item parameters
        initialProvider = request.POST.get('ip')
        itemID = request.POST.get('id')
        asin = request.POST.get('aid')
        gbombID = request.POST.get('gid')

        itemName = request.POST.get('n')
        releaseDate = request.POST.get('rd')
        platform = request.POST.get('p')
        smallImage = request.POST.get('si')
        thumbnailImage = request.POST.get('ti')
        largeImage = request.POST.get('li')

        metacriticPage = request.POST.get('mp')
        metascore = request.POST.get('ms')

        gameStatus = request.POST.get('gs')
        playStatus = request.POST.get('ps')
        userRating = request.POST.get('ur')

        # authentication
        userID = request.POST.get('uid')
        secretKey = request.POST.get('uk')

        # prevent demo account
        if (secretKey == '1'):
            return HttpResponse(simplejson.dumps({'status': 'demo'}), mimetype='application/json')

        # get user by userid
        try:
            existingUser = Users.objects.get(pk=userID, user_secret_key=secretKey)
        except Users.DoesNotExist:
            existingUser = None

        # get existing item
        try:
            item = Items.objects.get(pk=itemID, user=existingUser)
        except Items.DoesNotExist:
            item = None

        # validate secretKey against user
        if existingUser and item is not None:

            # update item
            item.item_initialProvider = initialProvider
            item.item_asin = asin
            item.item_gbombID = gbombID
            item.item_name = itemName
            item.item_releasedate = releaseDate
            item.item_platform = platform
            item.item_smallImage = smallImage
            item.item_thumbnailImage = thumbnailImage
            item.item_largeImage = largeImage
            item.item_metacriticPage = metacriticPage
            item.item_metascore = metascore
            item.item_gameStatus = gameStatus
            item.item_playStatus = playStatus
            item.item_userRating = userRating

            item.save()

            return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')

        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# UPDATE METACRITIC INFO
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def updateMetacritic(request):

    if (request.POST):

        # collect list item parameters
        itemID = request.POST.get('id')
        metacriticPage = request.POST.get('mp')
        metascore = request.POST.get('ms')

        # authentication
        userID = request.POST.get('uid')
        secretKey = request.POST.get('uk')

        # get user by userid
        try:
            existingUser = Users.objects.get(pk=userID, user_secret_key=secretKey)
        except Users.DoesNotExist:
            existingUser = None

        # get existing item
        try:
            item = Items.objects.get(pk=itemID, user=existingUser)
        except Items.DoesNotExist:
            item = None

        # validate secretKey against user
        if existingUser and item is not None:

            # update item
            item.item_metacriticPage = metacriticPage
            item.item_metascore = metascore

            item.save()

            return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')

        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# READ ITEMS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def getListItems(request):

    if (request.POST):

        # collect list item parameters
        userID = request.POST.get('user_id')
        secretKey = request.POST.get('uk')
        tagID = request.POST.get('list_id')

        # get user by userid
        try:
            existingUser = Users.objects.get(pk=userID)
        except Users.DoesNotExist:
            existingUser = None

        # get existing list by tagID
        try:
            existingTag = Tags.objects.get(pk=tagID)
        except Tags.DoesNotExist:
            existingTag = None

        # validate secretKey against user
        if existingUser and (existingTag or tagID == '0') and existingUser.user_secret_key == secretKey:

            itemDictionary = {'items': []}

            # get tag items
            try:
                # items for all tags
                if tagID == '0':
                    itemTagUsers = ItemTagUser.objects.filter(user=existingUser)
                # items filtered by tag
                else:
                    itemTagUsers = ItemTagUser.objects.filter(user=existingUser, tag=existingTag)

            except ItemTagUser.DoesNotExist:
                itemTagUsers = None

            # list items found
            if itemTagUsers:

                usersListItems = []
                addedItemIDs = []

                # construct python dictionary
                for items in itemTagUsers:

                    if (items.item.pk not in addedItemIDs):

                        # add item to userListItems
                        usersListItems.append({
                            'id': items.item.pk,
                            'ip': items.item.item_initialProvider,
                            'iid': items.item.pk,
                            'aid': items.item.item_asin,
                            'gid': items.item.item_gbombID,
                            'n': items.item.item_name,
                            'rd': str(items.item.item_releasedate),
                            'p': items.item.item_platform,
                            'si': items.item.item_smallImage,
                            'ti': items.item.item_thumbnailImage,
                            'li': items.item.item_largeImage,
                            'ms': items.item.item_metascore,
                        })

                        # add to list of itemIDs added - prevent multiple distinct items (by itemID) from appearing in 'view all list'
                        addedItemIDs.append(items.item.pk)

                itemDictionary = {'items': usersListItems}

                # serialize and return lists
                return HttpResponse(simplejson.dumps(itemDictionary), mimetype='application/json')

            else:

                return HttpResponse(simplejson.dumps(itemDictionary), mimetype='application/json')
        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# GET DIRECTORY OF ID/3RD PARTY IDs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def getDirectory(request):

    if (request.POST):

        # collect list item parameters
        userID = request.POST.get('user_id')
        secretKey = request.POST.get('uk')

        # get user by userid
        try:
            existingUser = Users.objects.get(pk=userID)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser and existingUser.user_secret_key == secretKey:

            # get tag items
            try:
                itemTagUsers = ItemTagUser.objects.filter(user=existingUser)
            except ItemTagUser.DoesNotExist:
                itemTagUsers = None

            # list items found
            if itemTagUsers:

                directoryItems = {}
                # construct python dictionary
                for items in itemTagUsers:

                    # create item object
                    if items.item.pk not in directoryItems:
                        directoryItems[items.item.pk] = {
                            'aid': items.item.item_asin,
                            'gid': items.item.item_gbombID,
                            'gs': items.item.item_gameStatus,
                            'ps': items.item.item_playStatus,
                            'ur': items.item.item_userRating,
                            't': {},
                            'tc': 0
                        }

                    # append tag
                    directoryItems[items.item.pk]['t'][items.tag.pk] = items.pk
                    directoryItems[items.item.pk]['tc'] = directoryItems[items.item.pk]['tc'] + 1

                # serialize and return lists
                return HttpResponse(simplejson.dumps({'directory': directoryItems}), mimetype='application/json')

            else:
                return HttpResponse(simplejson.dumps({'status': 'empty'}), mimetype='application/json')
        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# GET TAGS FOR ITEM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def getItemTags(request):

    if (request.POST):

        # collect list item parameters
        userID = request.POST.get('user_id')
        secretKey = request.POST.get('uk')
        itemID = request.POST.get('item_id')

        # get user by userid
        try:
            existingUser = Users.objects.get(pk=userID)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser and existingUser.user_secret_key == secretKey:

            # get item tags
            try:
                itemTagUsers = ItemTagUser.objects.filter(user=existingUser, item=itemID)
            except ItemTagUser.DoesNotExist:
                itemTagUsers = None

            # list items found
            if itemTagUsers:

                itemTags = []
                # construct python dictionary
                for items in itemTagUsers:
                    itemTags.append({'id': items.pk, 'tagID': items.tag.pk})

                tagDictionary = {'itemTags': itemTags}

                # serialize and return lists
                return HttpResponse(simplejson.dumps(tagDictionary), mimetype='application/json')

            else:
                return HttpResponse('FALSE', mimetype='text/html')
        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# GET ITEM TAGS BY 3RD PARTY ID
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def getItemTagsByThirdPartyID(request):

    if (request.POST):

        # collect list item parameters
        userID = request.POST.get('user_id')
        secretKey = request.POST.get('uk')
        itemID = request.POST.get('item_id')

        # get user by userid
        try:
            existingUser = Users.objects.get(pk=userID)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser and existingUser.user_secret_key == secretKey:

            # get item tags
            try:
                itemTagUsers = ItemTagUser.objects.filter(user=existingUser, item=itemID)
            except ItemTagUser.DoesNotExist:
                itemTagUsers = None

            # list items found
            if itemTagUsers:

                itemTags = []
                # construct python dictionary
                for items in itemTagUsers:
                    itemTags.append({'id': items.pk, 'tagID': items.tag.pk})

                tagDictionary = {'itemTags': itemTags}

                # serialize and return lists
                return HttpResponse(simplejson.dumps(tagDictionary), mimetype='application/json')

            else:
                return HttpResponse('FALSE', mimetype='text/html')
        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# DELETE ITEM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def deleteListItem(request):

    if (request.POST):

        # collect item parameters
        userID = request.POST.get('user_id')
        secretKey = request.POST.get('uk')

        id = request.POST.get('id')

        # get user by userid
        try:
            existingUser = Users.objects.get(pk=userID, user_secret_key=secretKey)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser:

            # get element to delete from ItemTagUser
            try:
                itemTagUser = ItemTagUser.objects.get(pk=id, user=existingUser)
            except ItemTagUser.DoesNotExist:
                itemTagUser = None

            # found record > delete
            if itemTagUser:
                tagID = itemTagUser.tag.pk

                # prevent demo account from saving data
                if (secretKey != '1'):
                    itemTagUser.delete()

                return HttpResponse(simplejson.dumps({'tagID': tagID}), mimetype='application/json')

            return HttpResponse(simplejson.dumps({'status': 'record not found'}), mimetype='application/json')

        else:
            return HttpResponse(simplejson.dumps({'status': 'user not found'}), mimetype='application/json')

    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# DELETE ITEMS IN BATCH
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def deleteListItemsInBatch(request):

    if (request.POST):

        # collect item parameters
        userID = request.POST.get('user_id')
        secretKey = request.POST.get('uk')

        ids = request.POST.getlist('ids[]')

        # get user by userid
        try:
            existingUser = Users.objects.get(pk=userID, user_secret_key=secretKey)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser:

            itemsDeleted = []

            for id in ids:
                # get element to delete from ItemTagUser
                try:
                    itemTagUser = ItemTagUser.objects.get(pk=id, user=existingUser)
                except ItemTagUser.DoesNotExist:
                    itemTagUser = None

                # found record > delete
                if itemTagUser:
                    # add to list of items deleted
                    itemsDeleted.append({'id': itemTagUser.pk, 'tagID': itemTagUser.tag.pk})

                    # prevent demo account from saving data
                    if (secretKey != '1'):
                        itemTagUser.delete()

            return HttpResponse(simplejson.dumps({'itemsDeleted': itemsDeleted}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'user not found'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')
