from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils import simplejson

import urllib
import urllib2
import bottlenose
import random
import hashlib
import time
import uuid

# database models
from tmz.models import Users, Items, Tags, ItemTagUser

# amazon api properties
accessKey = '0JVZGYMSKN59DPNKRGR2'
secretKey = 'AImptXlEmeKcQREmkl6qCEomGnm7aoueigTOJlmL'
associate_tag = 'codeco06-20'
xml2JSON = 'http://xml2json-xslt.googlecode.com/svn/trunk/xml2json.xslt'

# giantbomb api properties
giantBombAPIKey = 'e89927b08203137d0252fbf1f611a38489edb208'


# index page
def index(request):
    return render_to_response('index.html', {'random': random.random()})


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METACRITIC
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def itemSearchMetacritic(request):

    if 'keywords' in request.GET:
        keywords = request.GET.get('keywords')

    # http://www.metacritic.com/search/game/something/results
    url = 'http://www.metacritic.com/search/game/' + keywords + '/results'
    req = urllib2.Request(url)
    f = urllib2.urlopen(req)

    return HttpResponse(f.read(), mimetype='text/html')


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

    # Availability='Available', Condition='All', MerchantId='Amazon', MinimumPrice='800', MaximumPrice='13500'
    if browseNode == '0':
        response = amazon.ItemSearch(SearchIndex=searchIndex, Title=keywords, ResponseGroup=responseGroup, ItemPage=page, Sort='salesrank')
    else:
        response = amazon.ItemSearch(SearchIndex=searchIndex, Title=keywords, ResponseGroup=responseGroup, ItemPage=page, Sort='salesrank', MinimumPrice='800', MaximumPrice='13500', BrowseNode=browseNode)

    return HttpResponse(response, mimetype='application/xml')


# item detail by asin
def itemDetailAmazon(request):

    if 'asin' in request.GET:
        asin = request.GET.get('asin')

    if 'response_group' in request.GET:
        responseGroup = request.GET.get('response_group')

    amazon = bottlenose.Amazon(accessKey, secretKey, associate_tag)
    response = amazon.ItemLookup(ItemId=asin, IdType='ASIN', ResponseGroup=responseGroup)

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
    req = urllib2.Request(api_string, headers={"Accept-Encoding": "gzip"})

    opener = urllib2.build_opener()
    f = opener.open(req)
    jsonResponse = simplejson.load(f)

    return jsonResponse


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

        if 'user_login' in request.POST and 'user_password' in request.POST:

            # get user parameters
            userLogin = request.POST.get('user_login')
            userPassword = request.POST.get('user_password')

            # hash password
            userPassword = hashlib.md5(userPassword).hexdigest()

            # validate login
            try:
                user = Users.objects.get(user_login = userLogin, user_password = userPassword)
            except Users.DoesNotExist:
                user = None

            if user:

                # generate secret key
                secretKey = hashlib.md5(userLogin)
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
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')


# CREATE USER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def createUser(request):

    if (request.POST):

        # collect user parameters
        userLogin = request.POST.get('user_login')
        userPassword = request.POST.get('user_password')
        userEmail = request.POST.get('user_email')

        # hash password
        userPassword = hashlib.md5(userPassword).hexdigest()

        # create user
        guid = str(uuid.uuid4())
        user = Users(id = guid, user_login = userLogin, user_password = userPassword, user_email = userEmail, user_secret_key = '')
        user.save()

        return HttpResponse('TRUE', mimetype='text/html')

    else:
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')


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
            user = Users.objects.get(pk = userID)
        except Users.DoesNotExist:
            user = None

        # validate secretKey against user
        if user and user.user_secret_key == secretKey:

            # create list
            guid = str(uuid.uuid4())
            newList = Tags(id = guid, user = user, list_name = listName)
            newList.save()

            returnData = {'listID': newList.pk, 'listName': listName}

            return HttpResponse(simplejson.dumps(returnData), mimetype='application/json')

        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')


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
            user = Users.objects.get(pk = userID)
        except Users.DoesNotExist:
            user = None

        # validate secretKey against user
        if user and user.user_secret_key == secretKey:

            # get lists
            try:
                lists = Tags.objects.filter(user = user)
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
                return HttpResponse('FALSE', mimetype='text/html')
        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')


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

        # get user by userid
        try:
            existingUser = Users.objects.get(pk = userID, user_secret_key = secretKey)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser:

            # get all ItemTagUser entries in List
            try:
                itemTagUser = ItemTagUser.objects.filter(tag = tagID, user = existingUser)
            except ItemTagUser.DoesNotExist:
                itemTagUser = None

            # get tag entry
            try:
                tag = Tags.objects.get(pk = tagID, user = existingUser)
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
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')

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

        # get listIDs as array
        listIDs = request.POST.getlist('lids[]')

        # authentication
        userID = request.POST.get('uid')
        secretKey = request.POST.get('uk')

        # get user by userid
        try:
            existingUser = Users.objects.get(pk = userID)
        except Users.DoesNotExist:
            existingUser = None

        # get existing item
        try:
            existingItem = None
            if asin != '0':
                existingItem = Items.objects.get(item_asin = asin, user = existingUser)
            elif gbombID != '0':
                existingItem = Items.objects.get(item_gbombID = gbombID, user = existingUser)

        except Items.DoesNotExist:
            existingItem = None

        # get existing tags by tagID
        try:
            newTags = []
            for listID in listIDs:
                existingTag = Tags.objects.get(pk = listID)

                # if user, tag, item combination exists skip adding to new tag list
                try:
                    ItemTagUser.objects.get(user = existingUser, tag = existingTag, item = existingItem)
                except ItemTagUser.DoesNotExist:
                    newTags.append(existingTag)

        except Tags.DoesNotExist:
            newTags = None

        # validate secretKey against user
        if existingUser and newTags and existingUser.user_secret_key == secretKey:

            # create new item
            if (existingItem is None):
                guid = str(uuid.uuid4())
                item = Items(
                    id = guid,
                    user = existingUser,
                    item_initialProvider = initialProvider,
                    item_asin = asin,
                    item_gbombID = gbombID,
                    item_name = itemName,
                    item_releasedate = releaseDate,
                    item_platform = platform,
                    item_smallImage = smallImage,
                    item_thumbnailImage = thumbnailImage,
                    item_largeImage = largeImage,
                    item_metacriticPage = metacriticPage,
                    item_metascore = metascore,
                    item_gameStatus = gameStatus,
                    item_playStatus = playStatus,
                    item_userRating = userRating
                )
                item.save()

            # item already exists, use instead
            else:
                item = existingItem

            # create link between Item, Tag and User for multiple tags
            tagIDsAdded = []
            idsAdded = []

            for existingTag in newTags:
                guid = str(uuid.uuid4())
                link = ItemTagUser(id = guid, user = existingUser, tag = existingTag, item = item)
                link.save()

                # record item ids and tag ids that have been added
                tagIDsAdded.append(existingTag.pk)
                idsAdded.append(link.pk)

            returnData = {'idsAdded': idsAdded, 'itemID': item.pk, 'tagIDsAdded': tagIDsAdded}

            return HttpResponse(simplejson.dumps(returnData), mimetype='application/json')

        else:
            return HttpResponse('FALSE', mimetype='text/html')

    else:
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')


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

        # get user by userid
        try:
            existingUser = Users.objects.get(pk = userID, user_secret_key = secretKey)
        except Users.DoesNotExist:
            existingUser = None

        # get existing item
        try:
            item = Items.objects.get(pk = itemID, user = existingUser)
        except Items.DoesNotExist:
            item = None

        # validate secretKey against user
        if existingUser:

            # create new item
            if (item is not None):
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
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')


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
            existingUser = Users.objects.get(pk = userID)
        except Users.DoesNotExist:
            existingUser = None

        # get existing list by tagID
        try:
            existingTag = Tags.objects.get(pk = tagID)
        except Tags.DoesNotExist:
            existingTag = None

        # validate secretKey against user
        if existingUser and (existingTag or tagID == '0') and existingUser.user_secret_key == secretKey:

            # get tag items
            try:
                # items for all tags
                if tagID == '0':
                    itemTagUsers = ItemTagUser.objects.filter(user = existingUser)
                # items filtered by tag
                else:
                    itemTagUsers = ItemTagUser.objects.filter(user = existingUser, tag = existingTag)

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
                            'id': items.pk,
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
                        })

                        # add to list of itemIDs added - prevent multiple distinct items (by itemID) from appearing in 'view all list'
                        addedItemIDs.append(items.item.pk)

                itemDictionary = {'items': usersListItems}

                # serialize and return lists
                return HttpResponse(simplejson.dumps(itemDictionary), mimetype='application/json')

            else:
                return HttpResponse('FALSE', mimetype='text/html')
        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')


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
            existingUser = Users.objects.get(pk = userID)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser and existingUser.user_secret_key == secretKey:

            # get tag items
            try:
                itemTagUsers = ItemTagUser.objects.filter(user = existingUser)
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
                return HttpResponse('FALSE', mimetype='text/html')
        else:
            return HttpResponse('FALSE', mimetype='text/html')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')


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
            existingUser = Users.objects.get(pk = userID)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser and existingUser.user_secret_key == secretKey:

            # get item tags
            try:
                itemTagUsers = ItemTagUser.objects.filter(user = existingUser, item = itemID)
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
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')


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
            existingUser = Users.objects.get(pk = userID)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser and existingUser.user_secret_key == secretKey:

            # get item tags
            try:
                itemTagUsers = ItemTagUser.objects.filter(user = existingUser, item = itemID)
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
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')


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
            existingUser = Users.objects.get(pk = userID, user_secret_key = secretKey)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser:

            # get element to delete from ItemTagUser
            try:
                itemTagUser = ItemTagUser.objects.get(pk = id, user = existingUser)
            except ItemTagUser.DoesNotExist:
                itemTagUser = None

            # found record > delete
            if itemTagUser:
                tagID = itemTagUser.tag.pk
                itemTagUser.delete()
                return HttpResponse(simplejson.dumps({'tagID': tagID}), mimetype='application/json')

            return HttpResponse(simplejson.dumps({'status': 'record not found'}), mimetype='application/json')

        else:
            return HttpResponse(simplejson.dumps({'status': 'user not found'}), mimetype='application/json')

    else:
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')


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
            existingUser = Users.objects.get(pk = userID, user_secret_key = secretKey)
        except Users.DoesNotExist:
            existingUser = None

        # validate secretKey against user
        if existingUser:

            itemsDeleted = []

            for id in ids:
                # get element to delete from ItemTagUser
                try:
                    itemTagUser = ItemTagUser.objects.get(pk = id, user = existingUser)
                except ItemTagUser.DoesNotExist:
                    itemTagUser = None

                # found record > delete
                if itemTagUser:
                    # add to list of items deleted
                    itemsDeleted.append({'id': itemTagUser.pk, 'tagID': itemTagUser.tag.pk})
                    itemTagUser.delete()

            return HttpResponse(simplejson.dumps({'itemsDeleted': itemsDeleted}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'user not found'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not POST request'}), mimetype='application/json')
