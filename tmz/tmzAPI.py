from django.http import HttpResponse
from google.appengine.api import mail
from google.appengine.ext import ndb

import hashlib
import datetime
import time
import random
import json
import uuid

import logging

# database models
from tmz.models import Users, Items, Tags, ItemTagUser

import gameSources

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# T_MINUS ZERO REST API
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# USER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# LOGIN #DONE#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def login(request):

    if (request.POST):

        if all(k in request.POST for k in ('user_email', 'user_password')):

            # get user parameters
            userEmail = request.POST.get('user_email')
            userPassword = request.POST.get('user_password')

            # hash password
            userPassword = hashlib.md5(userPassword).hexdigest()

            # validate login
            user = Users.query(Users.user_email == userEmail, Users.user_password == userPassword).get()

            if user:

                # generate secret key
                secretKey = hashlib.md5(userEmail)
                secretKey.update(str(time.time()))
                secretKey = secretKey.hexdigest()

                # save secret key
                user.user_secret_key = secretKey
                user.put()

                # construct json return object
                data = {'status': 'success', 'userID': user.key.urlsafe(), 'secretKey': secretKey, 'timestamp': user.user_update_timestamp, 'userName': user.user_name}

                return HttpResponse(json.dumps(data), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'invalid_login'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# LOGOUT #DONE#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def logout(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk')):

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')

            # get user by userid
            user = ndb.Key(urlsafe=userID).get()

            if user and user.user_secret_key == secretKey:

                # set key back to '1' for demo user
                if user.user_admin == True:
                    secretKey = '1'

                # generate secret key
                else:
                    secretKey = hashlib.md5(userID)
                    secretKey.update(str(time.time()))
                    secretKey = secretKey.hexdigest()

                # save secret key
                user.user_secret_key = secretKey
                user.put()

                return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')

            else:
                return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# GET USER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def user(request):

    if (request.POST):

        if 'user_name' in request.POST:

            # get user parameters
            userName = request.POST.get('user_name')

            # find user
            user = Users.query(Users.user_name == userName).get()

            if user:
                # construct json return object
                data = {'status': 'success', 'userName': user.user_name}

                return HttpResponse(json.dumps(data), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'invalid_user'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# CREATE USER - #DONE#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def createUser(request):

    if (request.POST):

        if all(k in request.POST for k in ('user_email', 'user_password')):

            # collect user parameters
            userEmail = request.POST.get('user_email')
            userPassword = request.POST.get('user_password')

            # check existing email
            user = Users.query(Users.user_email == userEmail).get()

            # user does not exist: create new user
            if user == None:
                # hash password
                userPassword = hashlib.md5(userPassword).hexdigest()

                # create user
                # generate username
                username = generateUsername(userEmail)

                # generate secret key
                secretKey = hashlib.md5(userEmail)
                secretKey.update(str(time.time()))
                secretKey = secretKey.hexdigest()

                # create user
                user = Users(user_email=userEmail, user_password=userPassword, user_secret_key=secretKey, user_name=username)

                if userEmail == 'demo@gamedex.net':
                    user.user_admin = True

                userKey = user.put()

                # create default list
                newList = Tags(user=userKey, list_name='wishlist')
                newList.put()

                # construct json return object
                data = {'status': 'success', 'userID': userKey.urlsafe(), 'secretKey': secretKey, 'userName': username}

                return HttpResponse(json.dumps(data), mimetype='application/json')

            # user exists
            else:
                return HttpResponse(json.dumps({'status': 'user_exists'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# GENERATE USERNAME
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def generateUsername(email):

    name = email.split('@')[0]

    # hash email address and pull first 3 digits
    emailHash = str(int(hashlib.md5(email).hexdigest(), 16))[0:3]

    # combine name and hash
    username = name + emailHash

    return username

# DELETE USER #DONE#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def deleteUser(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'user_password')):

            userID = request.POST.get('uid')
            userPassword = request.POST.get('user_password')

            # hash password
            userPassword = hashlib.md5(userPassword).hexdigest()

            # get user
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            # validate user password
            if user and user.user_password == userPassword:

                # delete itemTagUser for user
                itemTagUserQuery = ItemTagUser.query(ItemTagUser.user == userKey).fetch()
                itemTagUserKeys = []

                if (itemTagUserQuery):

                    for itemTagUser in itemTagUserQuery:
                        itemTagUserKeys.append(itemTagUser.key)

                    ndb.delete_multi(itemTagUserKeys)


                # delete tags for user
                tagsQuery = Tags.query(Tags.user == userKey).fetch()
                tagKeys = []

                if (tagsQuery):

                    for tag in tagsQuery:
                        tagKeys.append(tag.key)

                    ndb.delete_multi(tagKeys)

                # delete user
                user.key.delete()

                return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'incorrect_password'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# UPDATE USER
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateUser(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'user_password')):

            userID = request.POST.get('uid')
            userPassword = request.POST.get('user_password')

            # hash password
            userPassword = hashlib.md5(userPassword).hexdigest()

            # get user
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            # validate user password
            if user and user.user_password == userPassword:

                save = False

                # update user
                if 'user_email' in request.POST:
                    user.user_email = request.POST.get('user_email')
                    save = True
                if 'user_name' in request.POST:
                    new_user_name = request.POST.get('user_name')

                    existingUser = Users.query(Users.user_name == new_user_name).get()

                    # no user by that user name - continue to save
                    if (existingUser == None):
                        user.user_name = request.POST.get('user_name')
                        save = True

                    # user name exists > return status error
                    else:
                        return HttpResponse(json.dumps({'status': 'username_exists'}), mimetype='application/json')

                if 'user_new_password' in request.POST:
                    userNewPassword = request.POST.get('user_new_password')
                    user.user_password = hashlib.md5(userNewPassword).hexdigest()
                    save = True

                if (save):
                    user.put()

                return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'incorrect_password'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# SEND PASSWORD RESET CODE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def sendResetCode(request):

    if (request.POST):

        if 'user_email' in request.POST:

            email = request.POST.get('user_email')

            # get user by email
            user = Users.query(Users.user_email == email).get()

            # send email with reset code parameter
            if mail.is_email_valid(email):

                if user:

                    # create reset code
                    random.seed()
                    resetCode = str(random.randint(100, 999))

                    # save code to user record
                    user.user_reset_code = resetCode
                    user.put()

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

                    return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')

            return HttpResponse(json.dumps({'status': 'invalid_email'}), mimetype='application/json')
        # user_mail not in request
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# SUBMIT PASSWORD RESET CODE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def submitResetCode(request):

    if (request.POST):

        if all(k in request.POST for k in ('user_email', 'user_reset_code')):

            email = request.POST.get('user_email')
            resetCode = request.POST.get('user_reset_code')

            # get user by email and reset code
            user = Users.query(Users.user_email == email).get()

            if user and user.user_reset_code == resetCode:
                return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'incorrect_code'}), mimetype='application/json')

        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# UPDATE PASSWORD
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updatePassword(request):

    if (request.POST):

        if all(k in request.POST for k in ('user_email', 'user_new_password', 'user_reset_code')):

            email = request.POST.get('user_email')
            newPassword = request.POST.get('user_new_password')
            resetCode = request.POST.get('user_reset_code')

            # validate login
            user = Users.query(Users.user_email == email).get()

            if user and user.user_reset_code == resetCode:

                # remove reset code from user record
                user.user_reset_code = ''
                # update user password
                user.user_password = hashlib.md5(newPassword).hexdigest()
                user.put()

                return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'user_not_found'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TAGS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# CREATE TAG #DONE#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def createList(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'tag_name', 'ts')):

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            tagName = request.POST.get('tag_name').strip().lower()
            updateTimestamp = request.POST.get('ts')

            # get user by userid
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            if user and user.user_secret_key == secretKey:

                # get list
                listItem = Tags.query(Tags.list_name == tagName, Tags.user == userKey).get()

                if listItem == None:

                    # set new timestamp
                    user.user_update_timestamp = updateTimestamp
                    user.put()

                    # create list
                    listItem = Tags(user=userKey, list_name=tagName)

                    # prevent demo account from saving data
                    if (secretKey != '1'):
                        listItem.put()

                returnData = {'tagID': listItem.key.urlsafe(), 'tagName': tagName}

                return HttpResponse(json.dumps(returnData), mimetype='application/json')

            else:
                return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')

        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# READ TAGS #DONE#
# return a list of tags
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getList(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk')) or 'user_name' in request.POST:

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')

            # get user by username
            if 'user_name' in request.POST:
                userName = request.POST.get('user_name')

                user = Users.query(Users.user_name == userName).get()

            # get user by userid
            else:
                userKey = ndb.Key(urlsafe=userID)
                user = userKey.get()

            # user found
            if user and user.user_secret_key == secretKey:

                listDictionary = {'list': []}

                # get lists
                lists = Tags.query(Tags.user == user.key).fetch()

                # lists found
                if lists:

                    usersList = []
                    # construct python dictionary
                    for item in lists:
                        usersList.append({'tagID': item.key.urlsafe(), 'tagName': item.list_name})

                    listDictionary = {'list': usersList}

                    # serialize and return lists
                    return HttpResponse(json.dumps(listDictionary), mimetype='application/json')

                else:
                    return HttpResponse(json.dumps(listDictionary), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# UPDATE TAG #DONE#
# update tag name
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateList(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'tag_name', 'tag_id', 'ts')):

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            tagName = request.POST.get('tag_name').strip()
            tagID = request.POST.get('tag_id')
            updateTimestamp = request.POST.get('ts')

            # prevent demo account
            if (secretKey == '1'):
                return HttpResponse(json.dumps({'status': 'demo'}), mimetype='application/json')

            # get user by userid
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            # validate user secret key
            if user and user.user_secret_key == secretKey:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.put()

                # get list
                ItemTagUser.user == userKey

                tagKey = ndb.Key(urlsafe=tagID)
                tag = Tags.query(Tags.key == tagKey, Tags.user == userKey).get()

                # tag found
                if tag:

                    tag.list_name = tagName
                    tag.put()

                    return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')

                else:
                    return HttpResponse(json.dumps({'status': 'not found'}), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# DELETE TAG #DONE#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
                return HttpResponse(json.dumps({'status': 'demo'}), mimetype='application/json')

            # get user by userid
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            # validate secret key
            if user and user.user_secret_key == secretKey:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.put()

                # get all ItemTagUser entries in List
                tagKey = ndb.Key(urlsafe=tagID)

                itemTagUserQuery = ItemTagUser.query(ItemTagUser.tag == tagKey, ItemTagUser.user == userKey).fetch()
                itemTagUserKeys = []

                if (itemTagUserQuery):

                    for itemTagUser in itemTagUserQuery:
                        itemTagUserKeys.append(itemTagUser.key)

                    ndb.delete_multi(itemTagUserKeys)

                # get tag entry
                tag = tagKey.get()

                if tag:
                    tag.key.delete()

                    return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')

                return HttpResponse(json.dumps({'status': 'no_record'}), mimetype='application/json')

            else:
                return HttpResponse(json.dumps({'status': 'no_user'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ITEMS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# CREATE ITEM #DONE#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
            imageBaseURL = request.POST.get('ib')
            smallImage = request.POST.get('si')
            thumbnailImage = request.POST.get('ti')
            largeImage = request.POST.get('li')

            metacriticPage = request.POST.get('mp')
            metascore = request.POST.get('ms')

            amazonPrice = request.POST.get('ap')
            amazonNewPrice = request.POST.get('anp')
            amazonUsedPrice = request.POST.get('aup')
            steamPrice = request.POST.get('sp')

            amazonPriceURL = request.POST.get('apu')
            amazonNewPriceURL = request.POST.get('anpu')
            amazonUsedPriceURL = request.POST.get('aupu')
            steamPriceURL = request.POST.get('spu')

            # optional game properties
            if all(k in request.POST for k in ('gs', 'ps', 'ur')):
                gameStatus = request.POST.get('gs')
                playStatus = request.POST.get('ps')
                userRating = request.POST.get('ur')
            else:
                gameStatus = '0'
                playStatus = '0'
                userRating = '0'

            # get tagIDs as array
            tagIDs = request.POST.getlist('lids[]')

            # authentication
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            updateTimestamp = request.POST.get('ts')

            # get user by userid
            itemKeyURLSafe = str(uuid.uuid4())
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            # get existing item based on initial provider
            existingItem = None

            # amazon provider
            if initialProvider == '0':
                existingItem = Items.query(Items.item_asin == asin, Items.item_initialProvider == '0').get()
            # giantbomb provider
            elif initialProvider == '1':
                existingItem = Items.query(Items.item_gbombID == gbombID, Items.item_initialProvider == '1', Items.item_platform == platform).get()


            if user and user.user_secret_key == secretKey:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.put()

                # create new item
                if existingItem == None:

                    item = Items(
                        item_asin=asin,
                        item_gbombID=gbombID,
                        item_initialProvider=initialProvider,
                        item_name=itemName,
                        item_releasedate=datetime.datetime.strptime(releaseDate, '%Y-%m-%d').date(),
                        item_platform=platform,
                        item_imageBaseURL=imageBaseURL,
                        item_smallImage=smallImage,
                        item_thumbnailImage=thumbnailImage,
                        item_largeImage=largeImage,
                        item_metacriticPage=metacriticPage,
                        item_metascore=metascore,

                        item_amazonPrice=amazonPrice,
                        item_amazonNewPrice=amazonNewPrice,
                        item_amazonUsedPrice=amazonUsedPrice,
                        item_steamPrice=steamPrice,

                        item_amazonPriceURL=amazonPriceURL,
                        item_amazonNewPriceURL=amazonNewPriceURL,
                        item_amazonUsedPriceURL=amazonUsedPriceURL,
                        item_steamPriceURL=steamPriceURL,
                    )

                    # prevent demo account from saving data
                    if (secretKey != '1'):
                        itemKey = item.put()
                        itemKeyURLSafe = itemKey.urlsafe()

                # item already exists, use instead
                else:
                    item = existingItem
                    itemKey = existingItem.key
                    itemKeyURLSafe = itemKey.urlsafe()

                # create link between Item, Tag and User for multiple tags
                tagIDsAdded = []
                idsAdded = []

                for tagID in tagIDs:

                    # get tag
                    tagKey = ndb.Key(urlsafe=tagID)

                    # generate fake itemTagUserKey for demo
                    itemTagUserKey = str(uuid.uuid4())

                    # prevent demo account from saving data
                    if (secretKey != '1'):

                        # get existing ItemTagUser
                        itemTagUser = ItemTagUser.query(ItemTagUser.item == itemKey, ItemTagUser.tag == tagKey, ItemTagUser.user == userKey).get()

                        if itemTagUser == None:
                            # create link
                            link = ItemTagUser(
                                user=userKey,
                                tag=tagKey,
                                item=itemKey,
                                item_gameStatus=gameStatus,
                                item_playStatus=playStatus,
                                item_userRating=userRating,
                            )
                            itemTagUserKey = link.put()

                        else:
                            itemTagUserKey = itemTagUser.key

                        # convert to url safe
                        itemTagUserKey = itemTagUserKey.urlsafe()

                    # record item ids and tag ids that have been added
                    tagIDsAdded.append(tagKey.urlsafe())
                    idsAdded.append(itemTagUserKey)

                returnData = {'idsAdded': idsAdded, 'itemID': itemKeyURLSafe, 'tagIDsAdded': tagIDsAdded}

                return HttpResponse(json.dumps(returnData), mimetype='application/json')

            else:
                return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# UPDATE USER ITEM #DONE#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
                return HttpResponse(json.dumps({'status': 'demo'}), mimetype='application/json')

            # get user by userid
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            # get item key
            itemKey = ndb.Key(urlsafe=itemID)

            # get existing link
            itemTagUser = ItemTagUser.query(ItemTagUser.item == itemKey, ItemTagUser.user == userKey).fetch()

            # validate user secret key
            if user and user.user_secret_key == secretKey:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.put()

                # iterate all itemTagUser items and update attributes
                for link in itemTagUser:
                    link.item_gameStatus = gameStatus
                    link.item_playStatus = playStatus
                    link.item_userRating = userRating

                    link.put()

                return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')

            else:
                return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# UPDATE METACRITIC INFO #DONE#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            # get existing item
            itemKey = ndb.Key(urlsafe=itemID)
            item = itemKey.get()

            # validate user secret key
            if user and user.user_secret_key == secretKey:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.put()

                # update item
                item.item_metacriticPage = metacriticPage
                item.item_metascore = metascore

                item.put()

                return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')

            else:
                return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# UPDATE SHARED ITEM DATA
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateSharedItemPrice(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'ts')):

            # authentication
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            updateTimestamp = request.POST.get('ts')

            # collect list item parameters
            itemID = request.POST.get('id')

            if 'ap' in request.POST:
                amazonPrice = request.POST.get('ap')
                amazonPriceURL = request.POST.get('apu')
            if 'anp' in request.POST:
                amazonNewPrice = request.POST.get('anp')
                amazonNewPriceURL = request.POST.get('anpu')
            if 'aup' in request.POST:
                amazonUsedPrice = request.POST.get('aup')
                amazonUsedPriceURL = request.POST.get('aupu')
            if 'sp' in request.POST:
                steamPrice = request.POST.get('sp')
                steamPriceURL = request.POST.get('spu')

            # prevent demo account
            if (secretKey == '1'):
                return HttpResponse(json.dumps({'status': 'demo'}), mimetype='application/json')

            # get user by userid
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            # get existing item
            itemKey = ndb.Key(urlsafe=itemID)
            item = itemKey.get()

            # validate user secret key
            if user and user.user_secret_key == secretKey:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.put()

                # update item
                if amazonPrice and amazonPrice != '':
                    item.item_amazonPrice = amazonPrice
                    item.item_amazonPriceURL = amazonPriceURL

                if amazonNewPrice and amazonNewPrice != '':
                    item.item_amazonNewPrice = amazonNewPrice
                    item.item_amazonNewPriceURL = amazonNewPriceURL

                if amazonUsedPrice and amazonUsedPrice != '':
                    item.item_amazonUsedPrice = amazonUsedPrice
                    item.item_amazonUsedPriceURL = amazonUsedPriceURL

                if steamPrice and steamPrice != '':
                    item.item_steamPrice = steamPrice
                    item.item_steamPriceURL = steamPriceURL

                item.put()

                return HttpResponse(json.dumps({'status': 'success'}), mimetype='application/json')

            else:
                return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# READ ITEMS #DONE#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
                user = Users.query(Users.user_name == userName).get()

            # get user by userid
            else:
                userKey = ndb.Key(urlsafe=userID)
                user = userKey.get()


            # empty dictionary
            itemDictionary = {'items': []}

            # user found
            if user and user.user_secret_key == secretKey:

                # items for all tags
                if tagID == '0':
                    itemTagUsers = ItemTagUser.query(ItemTagUser.user == user.key).fetch()

                # items filtered by tag
                else:
                    existingTagKey = ndb.Key(urlsafe=tagID)
                    itemTagUsers = ItemTagUser.query(ItemTagUser.user == user.key, ItemTagUser.tag == existingTagKey).fetch()

                # list items found
                if itemTagUsers:

                    usersListItems = []
                    addedItemIDs = []

                    # construct python dictionary
                    for items in itemTagUsers:

                        item = items.item.get()

                        if (items.item.urlsafe() not in addedItemIDs):

                            # add item to userListItems
                            usersListItems.append({
                                'ip': item.item_initialProvider,
                                'iid': item.key.urlsafe(),
                                'aid': item.item_asin,
                                'gid': item.item_gbombID,
                                'n': item.item_name,
                                'rd': str(item.item_releasedate),
                                'p': item.item_platform,
                                'ib': item.item_imageBaseURL,
                                'si': item.item_smallImage,
                                'ti': item.item_thumbnailImage,
                                'li': item.item_largeImage,
                                'ms': item.item_metascore,
                                'mp': item.item_metacriticPage,

                                'ap': item.item_amazonPrice,
                                'anp': item.item_amazonNewPrice,
                                'aup': item.item_amazonUsedPrice,
                                'sp': item.item_steamPrice,

                                'apu': item.item_amazonPriceURL,
                                'anpu': item.item_amazonNewPriceURL,
                                'aupu': item.item_amazonUsedPriceURL,
                                'spu': item.item_steamPriceURL,
                            })

                            # add to list of itemIDs added - prevent multiple distinct items (by itemID) from appearing in 'view all list'
                            addedItemIDs.append(items.item.urlsafe())

                    itemDictionary = {'items': usersListItems}

                    # serialize and return lists
                    return HttpResponse(json.dumps(itemDictionary), mimetype='application/json')
                else:
                    return HttpResponse(json.dumps(itemDictionary), mimetype='application/json')
            else:
                return HttpResponse(json.dumps(itemDictionary), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# GET DIRECTORY OF ID/3RD PARTY IDs #DONE#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getDirectory(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk')) or 'user_name' in request.POST:

            # collect list item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')

            # get user by username
            if 'user_name' in request.POST:
                userName = request.POST.get('user_name')
                user = Users.query(Users.user_name == userName).get()

            # get user by userid
            else:
                userKey = ndb.Key(urlsafe=userID)
                user = userKey.get()

            if user and user.user_secret_key == secretKey:

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
            else:
                return HttpResponse('failed', mimetype='application/json', status='500')
        else:
            return HttpResponse('missing_param', mimetype='application/json', status='500')
    else:
        return HttpResponse('not_post', mimetype='application/json', status='500')


# GET TAGS FOR ITEM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

                user = Users.query(Users.user_name == userName).get()

            # get user by userid
            else:
                userKey = ndb.Key(urlsafe=userID)
                user = userKey.get()

            if user and user.user_secret_key == secretKey:

                itemKey = ndb.Key(urlsafe=itemID)
                itemTagUsers = ItemTagUser.query(ItemTagUser.user == user.key, ItemTagUser.item == itemKey).fetch()

                # list items found
                if itemTagUsers:

                    itemTags = []
                    # construct python dictionary
                    for items in itemTagUsers:
                        itemTags.append({'id': items.pk, 'tagID': items.tag.pk})

                    tagDictionary = {'itemTags': itemTags}

                    # serialize and return lists
                    return HttpResponse(json.dumps(tagDictionary), mimetype='application/json')

                else:
                    return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# GET ITEM TAGS BY 3RD PARTY ID
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
                user = Users.query(Users.user_name == userName).get()

            # get user by userid
            else:
                userKey = ndb.Key(urlsafe=userID)
                user = userKey.get()

            # validate user secret key
            if user and user.user_secret_key == secretKey:

                # get itemKey
                itemKey = ndb.Key(urlsafe=itemID)

                # get item tags
                itemTagUsers = ItemTagUser.query(ItemTagUser.user == user.key, ItemTagUser.item == itemKey).fetch()

                # list items found
                if itemTagUsers:

                    itemTags = []
                    # construct python dictionary
                    for items in itemTagUsers:
                        itemTags.append({'id': items.key.urlsafe(), 'tagID': items.tag.urlsafe()})

                    tagDictionary = {'itemTags': itemTags}

                    # serialize and return lists
                    return HttpResponse(json.dumps(tagDictionary), mimetype='application/json')

                else:
                    return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'failed'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# DELETE ITEM
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def deleteListItem(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'ts')):

            # collect item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            updateTimestamp = request.POST.get('ts')

            id = request.POST.get('id')

            # get user by userid
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            # validate user secret key
            if user and user.user_secret_key == secretKey:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.put()

                # get element to delete from ItemTagUser
                try:
                    itemTagUserKey = ndb.Key(urlsafe=id)
                    itemTagUser = ItemTagUser.query(ItemTagUser.key == itemTagUserKey, ItemTagUser.user == userKey).get()

                except Exception:
                    itemTagUser = None

                # found record > delete
                if itemTagUser and itemTagUser.user == userKey:
                    tagID = itemTagUser.tag.urlsafe()

                    # prevent demo account from saving data
                    if (secretKey != '1'):
                        itemTagUser.key.delete()

                    return HttpResponse(json.dumps({'tagID': tagID}), mimetype='application/json')

                return HttpResponse(json.dumps({'status': 'record not found'}), mimetype='application/json')

            else:
                return HttpResponse(json.dumps({'status': 'user not found'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# DELETE ITEMS IN BATCH
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def deleteListItemsInBatch(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'ts')):

            # collect item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            updateTimestamp = request.POST.get('ts')

            ids = request.POST.getlist('ids[]')

            # get user by userid
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            # validate user secret key
            if user and user.user_secret_key == secretKey:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.put()

                itemsDeleted = []

                for id in ids:
                    # get element to delete from ItemTagUser
                    itemTagUserKey = ndb.Key(urlsafe=id)
                    itemTagUser = ItemTagUser.query(ItemTagUser.key == itemTagUserKey, ItemTagUser.user == userKey).get()

                    # found record > delete
                    if itemTagUser and itemTagUser.user == userKey:
                        # add to list of items deleted
                        itemsDeleted.append({'id': itemTagUser.key.urlsafe(), 'tagID': itemTagUser.tag.urlsafe()})

                        # prevent demo account from saving data
                        if (secretKey != '1'):
                            itemTagUser.key.delete()

                return HttpResponse(json.dumps({'itemsDeleted': itemsDeleted}), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'user not found'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')


# IMPORT GAMES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def importGames(request):

    if (request.POST):

        if all(k in request.POST for k in ('uid', 'uk', 'ts', 'source', 'source_user')):

            # collect item parameters
            userID = request.POST.get('uid')
            secretKey = request.POST.get('uk')
            updateTimestamp = request.POST.get('ts')
            source = int(request.POST.get('source'))
            sourceUser = request.POST.get('source_user')

            # get user by userid
            userKey = ndb.Key(urlsafe=userID)
            user = userKey.get()

            # validate user secret key
            if user and user.user_secret_key == secretKey:

                # set new timestamp
                user.user_update_timestamp = updateTimestamp
                user.put()

                importedTitles = []

                # get user games from source

                # import Steam games
                if (source == 0):
                    logging.info('steam')

                    # get linked game information
                    importedTitles = gameSources.getSteamGames(sourceUser)

                # import PSN games
                elif (source == 1):
                    logging.info('PSN')

                    # get linked game information
                    importedTitles = gameSources.getPSNGames(sourceUser)

                # import Xbox Live Games
                elif (source == 2):
                    logging.info('XBL')

                    # get linked game information
                    importedTitles = gameSources.getXBLGames(sourceUser)


                return HttpResponse(json.dumps(importedTitles), mimetype='application/json')
            else:
                return HttpResponse(json.dumps({'status': 'user not found'}), mimetype='application/json')
        else:
            return HttpResponse('missing_param', mimetype='text/plain', status='500')
    else:
        return HttpResponse('not_post', mimetype='text/plain', status='500')
