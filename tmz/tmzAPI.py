from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import simplejson
from google.appengine.api import mail

import hashlib
import time
import uuid
import random

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

        if all(k in request.POST for k in ('user_email', 'user_password')):

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

                if userEmail == 'demo2@gamedex.net':
                    secretKey = '1'

                else:
                    # generate secret key
                    secretKey = hashlib.md5(userEmail)
                    secretKey.update(str(time.time()))
                    secretKey = secretKey.hexdigest()
                    # save secret key
                    user.user_secret_key = secretKey
                    user.save()

                # construct json return object
                data = {'status': 'success', 'userID': user.pk, 'secretKey': secretKey, 'timestamp': user.user_update_timestamp, 'userName': user.user_name}

                return HttpResponse(simplejson.dumps(data), mimetype='application/json')
            else:
                return HttpResponse(simplejson.dumps({'status': 'invalid_login'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


@csrf_exempt
def user(request):

    if (request.POST):

        if 'user_name' in request.POST:

            # get user parameters
            userName = request.POST.get('user_name')

            # find user
            try:
                user = Users.objects.get(user_name=userName)
            except Users.DoesNotExist:
                user = None

            if user:
                # construct json return object
                data = {'status': 'success', 'userName': user.user_name}

                return HttpResponse(simplejson.dumps(data), mimetype='application/json')
            else:
                return HttpResponse(simplejson.dumps({'status': 'invalid_user'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# CREATE USER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def createUser(request):

    if (request.POST):

        if all(k in request.POST for k in ('user_email', 'user_password')):

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
                user = Users(id=guid, user_email=userEmail, user_password=userPassword, user_secret_key='', user_name='')
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
                data = {'status': 'success', 'userID': user.pk, 'secretKey': secretKey}

                return HttpResponse(simplejson.dumps(data), mimetype='application/json')

            # user exists
            else:
                return HttpResponse(simplejson.dumps({'status': 'user_exists'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# UPDATE USER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def updateUser(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'user_password')):

            userID = request.POST.get('uid')
            userPassword = request.POST.get('user_password')

            # hash password
            userPassword = hashlib.md5(userPassword).hexdigest()

            # validate login
            try:
                user = Users.objects.get(pk=userID, user_password=userPassword)
            except Users.DoesNotExist:
                user = None

            if user:

                save = False

                # update user
                if 'user_email' in request.POST:
                    user.user_email = request.POST.get('user_email')
                    save = True
                if 'user_name' in request.POST:
                    user.user_name = request.POST.get('user_name')
                    save = True
                if 'user_new_password' in request.POST:
                    userNewPassword = request.POST.get('user_new_password')
                    user.user_password = hashlib.md5(userNewPassword).hexdigest()
                    save = True

                if (save):
                    user.save()

                return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')
            else:
                return HttpResponse(simplejson.dumps({'status': 'incorrect_password'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# SEND PASSWORD RESET CODE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def sendResetCode(request):

    if (request.POST):

        if 'user_email' in request.POST:

            email = request.POST.get('user_email')

            # get user by email
            try:
                user = Users.objects.get(user_email=email)
            except Users.DoesNotExist:
                user = None

            # send email with reset code parameter
            if mail.is_email_valid(email):

                if user:

                    # create reset code
                    random.seed()
                    resetCode = str(random.randint(100, 999))

                    # save code to user record
                    user.user_reset_code = resetCode
                    user.save()

                    message = mail.EmailMessage(sender='Gamedex.net <no-reply@gamedex.net>', subject='Gamedex.net: Password Reset Code')
                    message.to = email
                    message.body = """
Your password reset code for %s is:

%s

Please return to Gamedex.net and enter the 3-digit number above into the "Password Reset Code" field.
""" % (email, resetCode)

                    message.html = """
<html>

<head>
<title>Gamedex.net</title>
</head>

<body style="font-family: arial,sans-serif; margin: 10px 10px;"
<h3>Your password reset code for %s is:</h3>

<h1>%s</h1>

<h4>Please return to Gamedex.net and enter the 3-digit number above into the "Password Reset Code" field.</h4>
</body>
</html>
""" % (email, resetCode)
                    message.send()

                    return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')

                # user not found - do not reveal the registration status of email addresses > send success
                else:
                    return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')
            # invalid email - only checks that string is non-empty
            else:
                return HttpResponse(simplejson.dumps({'status': 'invalid_email'}), mimetype='application/json')
        # user_mail not in request
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# SUBMIT PASSWORD RESET CODE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def submitResetCode(request):

    if (request.POST):

        if all(k in request.POST for k in ('user_email', 'user_reset_code')):

            email = request.POST.get('user_email')
            resetCode = request.POST.get('user_reset_code')

            # get user by email and reset code
            try:
                user = Users.objects.get(user_email=email, user_reset_code=resetCode)
            except Users.DoesNotExist:
                user = None

            if user:
                return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')
            else:
                return HttpResponse(simplejson.dumps({'status': 'incorrect_code'}), mimetype='application/json')

        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# UPDATE PASSWORD
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def updatePassword(request):

    if (request.POST):

        if all(k in request.POST for k in ('user_email', 'user_new_password', 'user_reset_code')):

            email = request.POST.get('user_email')
            newPassword = request.POST.get('user_new_password')
            resetCode = request.POST.get('user_reset_code')

            # validate login
            try:
                user = Users.objects.get(user_email=email, user_reset_code=resetCode)
            except Users.DoesNotExist:
                user = None

            if user:

                # remove reset code from user record
                user.user_reset_code = ''
                # update user password
                user.user_password = hashlib.md5(newPassword).hexdigest()
                user.save()

                return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')
            else:
                return HttpResponse(simplejson.dumps({'status': 'user_not_found'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')

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

        if all(k in request.POST for k in ('uid', 'uk', 'tag_name', 'ts')):

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            listName = request.POST.get('tag_name').strip()
            updateTimestamp = request.POST.get('ts')

            # get user by userid
            try:
                user = Users.objects.get(pk=userID, user_secret_key=secretKey)
            except Users.DoesNotExist:
                user = None

            # validate secretKey against user
            if user:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.save()

                # create list
                guid = str(uuid.uuid4())
                newList = Tags(id=guid, user=user, list_name=listName)

                # prevent demo account from saving data
                if (secretKey != '1'):
                    newList.save()

                returnData = {'listID': newList.pk, 'listName': listName}

                return HttpResponse(simplejson.dumps(returnData), mimetype='application/json')

            else:
                return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')

        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# READ TAGS
# return a list of tags
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def getList(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk')) or 'user_name' in request.POST:

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')

            # get user by username
            if 'user_name' in request.POST:
                userName = request.POST.get('user_name')
                try:
                    user = Users.objects.get(user_name=userName)
                except Users.DoesNotExist:
                    user = None

            # get user by userid
            else:
                try:
                    user = Users.objects.get(pk=userID, user_secret_key=secretKey)
                except Users.DoesNotExist:
                    user = None

            # user found
            if user:

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
                return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# UPDATE TAG
# update tag name
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def updateList(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'tag_name', 'tag_id', 'ts')):

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            listName = request.POST.get('tag_name').strip()
            listID = request.POST.get('tag_id')
            updateTimestamp = request.POST.get('ts')

            # prevent demo account
            if (secretKey == '1'):
                return HttpResponse(simplejson.dumps({'status': 'demo'}), mimetype='application/json')

            # get user by userid
            try:
                user = Users.objects.get(pk=userID, user_secret_key=secretKey)
            except Users.DoesNotExist:
                user = None

            # validate secretKey against user
            if user:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.save()

                # get list
                try:
                    listItem = Tags.objects.get(pk=listID, user=user)
                except Tags.DoesNotExist:
                    listItem = None

                # listItem found
                if listItem:

                    listItem.list_name = listName
                    listItem.save()

                    return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')

                else:
                    return HttpResponse(simplejson.dumps({'status': 'not found'}), mimetype='application/json')
            else:
                return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# DELETE TAG
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def deleteList(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'ts', 'id')):

            # collect item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            updateTimestamp = request.POST.get('ts')

            tagID = request.POST.get('id')

            # prevent demo account
            if (secretKey == '1'):
                return HttpResponse(simplejson.dumps({'status': 'demo'}), mimetype='application/json')

            # get user by userid
            try:
                user = Users.objects.get(pk=userID, user_secret_key=secretKey)
            except Users.DoesNotExist:
                user = None

            # validate secretKey against user
            if user:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.save()

                # get all ItemTagUser entries in List
                try:
                    itemTagUser = ItemTagUser.objects.filter(tag=tagID, user=user)
                except ItemTagUser.DoesNotExist:
                    itemTagUser = None

                # get tag entry
                try:
                    tag = Tags.objects.get(pk=tagID, user=user)
                except Tags.DoesNotExist:
                    tag = None

                # found record(s) > delete ItemTagUser entries
                if itemTagUser:
                    itemTagUser.delete()

                if tag:
                    tag.delete()
                    return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')

                return HttpResponse(simplejson.dumps({'status': 'no_record'}), mimetype='application/json')

            else:
                return HttpResponse(simplejson.dumps({'status': 'no_user'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
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

        if all(k in request.POST for k in ('uid', 'uk', 'ts')):

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
            updateTimestamp = request.POST.get('ts')

            # get user by userid
            try:
                user = Users.objects.get(pk=userID, user_secret_key=secretKey)
            except Users.DoesNotExist:
                user = None

            # get existing item based on initial provider
            try:
                existingItem = None

                # amazon provider
                if initialProvider == '0':
                    existingItem = Items.objects.get(item_asin=asin, item_initialProvider='0')
                # giantbomb provider
                elif initialProvider == '1':
                    existingItem = Items.objects.get(item_gbombID=gbombID, item_initialProvider='1', item_platform=platform)

            except Items.DoesNotExist:
                existingItem = None

            # validate secretKey against user
            if user:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.save()

                # create new item
                if (existingItem is None):
                    guid = str(uuid.uuid4())
                    item = Items(
                        id=guid,
                        item_asin=asin,
                        item_gbombID=gbombID,
                        item_initialProvider=initialProvider,
                        item_name=itemName,
                        item_releasedate=releaseDate,
                        item_platform=platform,
                        item_smallImage=smallImage,
                        item_thumbnailImage=thumbnailImage,
                        item_largeImage=largeImage,
                        item_metacriticPage=metacriticPage,
                        item_metascore=metascore
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
                        link = ItemTagUser(
                            id=guid,
                            user=user,
                            tag=tag,
                            item=item,
                            item_gameStatus=gameStatus,
                            item_playStatus=playStatus,
                            item_userRating=userRating,
                        )
                        link.save()

                    # record item ids and tag ids that have been added
                    tagIDsAdded.append(tagID)
                    idsAdded.append(guid)

                returnData = {'idsAdded': idsAdded, 'itemID': item.pk, 'tagIDsAdded': tagIDsAdded}

                return HttpResponse(simplejson.dumps(returnData), mimetype='application/json')

            else:
                return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# UPDATE USER ITEM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def updateUserItem(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'ts')):

            # collect list item parameters
            itemID = request.POST.get('id')

            gameStatus = request.POST.get('gs')
            playStatus = request.POST.get('ps')
            userRating = request.POST.get('ur')

            # authentication
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            updateTimestamp = request.POST.get('ts')

            # prevent demo account
            if (secretKey == '1'):
                return HttpResponse(simplejson.dumps({'status': 'demo'}), mimetype='application/json')

            # get user by userid
            try:
                user = Users.objects.get(pk=userID, user_secret_key=secretKey)
            except Users.DoesNotExist:
                user = None

            # get existing link
            try:
                links = ItemTagUser.objects.filter(item=itemID, user=user)
            except ItemTagUser.DoesNotExist:
                links = None

            # validate secretKey against user
            if user and links is not None:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.save()

                # iterate all links items and update attributes
                for link in links:
                    link.item_gameStatus = gameStatus
                    link.item_playStatus = playStatus
                    link.item_userRating = userRating

                    link.save()

                return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')

            else:
                return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# UPDATE METACRITIC INFO
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def updateMetacritic(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'ts')):

            # collect list item parameters
            itemID = request.POST.get('id')
            metacriticPage = request.POST.get('mp')
            metascore = request.POST.get('ms')

            # authentication
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            updateTimestamp = request.POST.get('ts')

            # get user by userid
            try:
                user = Users.objects.get(pk=userID, user_secret_key=secretKey)
            except Users.DoesNotExist:
                user = None

            # get existing item
            try:
                item = Items.objects.get(pk=itemID)
            except Items.DoesNotExist:
                item = None

            # validate secretKey against user
            if user and item is not None:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.save()

                # update item
                item.item_metacriticPage = metacriticPage
                item.item_metascore = metascore

                item.save()

                return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')

            else:
                return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# UPDATE ITEM DATA
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def updateItem(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'ts')):

            # authentication
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            updateTimestamp = request.POST.get('ts')

            # collect list item parameters
            itemID = request.POST.get('id')
            asin = request.POST.get('aid')
            gbombID = request.POST.get('gid')

            releaseDate = request.POST.get('rd')
            smallImage = request.POST.get('si')
            thumbnailImage = request.POST.get('ti')
            largeImage = request.POST.get('li')

            # prevent demo account
            if (secretKey == '1'):
                return HttpResponse(simplejson.dumps({'status': 'demo'}), mimetype='application/json')

            # get user by userid
            try:
                user = Users.objects.get(pk=userID, user_secret_key=secretKey)
            except Users.DoesNotExist:
                user = None

            # get existing item
            try:
                item = Items.objects.get(pk=itemID)
            except Items.DoesNotExist:
                item = None

            # validate secretKey against user
            if user and item is not None:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.save()

                # update item
                item.item_asin = asin
                item.item_gbombID = gbombID
                item.item_releasedate = releaseDate
                item.item_smallImage = smallImage
                item.item_thumbnailImage = thumbnailImage
                item.item_largeImage = largeImage

                item.save()

                return HttpResponse(simplejson.dumps({'status': 'success'}), mimetype='application/json')

            else:
                return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# READ ITEMS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def getListItems(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk')) or 'user_name' in request.POST:

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            tagID = request.POST.get('list_id')

            # get user by username
            if 'user_name' in request.POST:
                userName = request.POST.get('user_name')
                try:
                    user = Users.objects.get(user_name=userName)
                except Users.DoesNotExist:
                    user = None

            # get user by userid
            else:
                try:
                    user = Users.objects.get(pk=userID, user_secret_key=secretKey)
                except Users.DoesNotExist:
                    user = None

            # get existing list by tagID
            try:
                existingTag = Tags.objects.get(pk=tagID)
            except Tags.DoesNotExist:
                existingTag = None

            # user found
            if user and (existingTag or tagID == '0'):

                itemDictionary = {'items': []}

                # get tag items
                try:
                    # items for all tags
                    if tagID == '0':
                        itemTagUsers = ItemTagUser.objects.filter(user=user)
                    # items filtered by tag
                    else:
                        itemTagUsers = ItemTagUser.objects.filter(user=user, tag=existingTag)

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
                return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# GET DIRECTORY OF ID/3RD PARTY IDs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def getDirectory(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk')) or 'user_name' in request.POST:

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')

            # get user by username
            if 'user_name' in request.POST:
                userName = request.POST.get('user_name')
                try:
                    user = Users.objects.get(user_name=userName)
                except Users.DoesNotExist:
                    user = None

            # get user by userid
            else:
                try:
                    user = Users.objects.get(pk=userID, user_secret_key=secretKey)
                except Users.DoesNotExist:
                    user = None

            # validate secretKey against user
            if user:

                # get tag items
                try:
                    itemTagUsers = ItemTagUser.objects.filter(user=user)
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
                                'gs': items.item_gameStatus,
                                'ps': items.item_playStatus,
                                'ur': items.item_userRating,
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
                return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# GET TAGS FOR ITEM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def getItemTags(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk')) or 'user_name' in request.POST:

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            itemID = request.POST.get('item_id')

            # get user by username
            if 'user_name' in request.POST:
                userName = request.POST.get('user_name')
                try:
                    user = Users.objects.get(user_name=userName)
                except Users.DoesNotExist:
                    user = None

            # get user by userid
            else:
                try:
                    user = Users.objects.get(pk=userID, user_secret_key=secretKey)
                except Users.DoesNotExist:
                    user = None

            # validate secretKey against user
            if user:

                # get item tags
                try:
                    itemTagUsers = ItemTagUser.objects.filter(user=user, item=itemID)
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
                    return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
            else:
                return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# GET ITEM TAGS BY 3RD PARTY ID
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def getItemTagsByThirdPartyID(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk')) or 'user_name' in request.POST:

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            itemID = request.POST.get('item_id')

            # get user by username
            if 'user_name' in request.POST:
                userName = request.POST.get('user_name')
                try:
                    user = Users.objects.get(user_name=userName)
                except Users.DoesNotExist:
                    user = None

            # get user by userid
            else:
                try:
                    user = Users.objects.get(pk=userID, user_secret_key=secretKey)
                except Users.DoesNotExist:
                    user = None

            # validate secretKey against user
            if user:

                # get item tags
                try:
                    itemTagUsers = ItemTagUser.objects.filter(user=user, item=itemID)
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
                    return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
            else:
                return HttpResponse(simplejson.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# DELETE ITEM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def deleteListItem(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'ts')):

            # collect item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            updateTimestamp = request.POST.get('ts')

            id = request.POST.get('id')

            # get user by userid
            try:
                user = Users.objects.get(pk=userID, user_secret_key=secretKey)
            except Users.DoesNotExist:
                user = None

            # validate secretKey against user
            if user:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.save()

                # get element to delete from ItemTagUser
                try:
                    itemTagUser = ItemTagUser.objects.get(pk=id, user=user)
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
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')


# DELETE ITEMS IN BATCH
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@csrf_exempt
def deleteListItemsInBatch(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'ts')):

            # collect item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            updateTimestamp = request.POST.get('ts')

            ids = request.POST.getlist('ids[]')

            # get user by userid
            try:
                user = Users.objects.get(pk=userID, user_secret_key=secretKey)
            except Users.DoesNotExist:
                user = None

            # validate secretKey against user
            if user:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.save()

                itemsDeleted = []

                for id in ids:
                    # get element to delete from ItemTagUser
                    try:
                        itemTagUser = ItemTagUser.objects.get(pk=id, user=user)
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
            return HttpResponse(simplejson.dumps({'status': 'missing_param'}), mimetype='application/json')
    else:
        return HttpResponse(simplejson.dumps({'status': 'not_post'}), mimetype='application/json')
