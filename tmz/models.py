from google.appengine.ext import ndb


# API KEYS
class ApiKeys(ndb.Model):
    keyName = ndb.StringProperty()
    keyValue = ndb.StringProperty()


# USERS
class Users(ndb.Model):
    id = ndb.KeyProperty()
    user_name = ndb.StringProperty(required=False)
    user_password = ndb.StringProperty()
    user_email = ndb.StringProperty()
    user_secret_key = ndb.StringProperty()
    user_reset_code = ndb.StringProperty(required=False)
    user_update_timestamp = ndb.StringProperty(required=False)

    user_account_created = ndb.DateTimeProperty(auto_now=False, auto_now_add=True)
    user_account_last_login = ndb.DateTimeProperty(auto_now=True, auto_now_add=True)


# TAGS
class Tags(ndb.Model):
    id = ndb.KeyProperty()
    user = ndb.KeyProperty(kind=Users)
    list_name = ndb.StringProperty()

    list_date_added = ndb.DateTimeProperty(auto_now=False, auto_now_add=True)
    list_date_last_modfied = ndb.DateTimeProperty(auto_now=True, auto_now_add=True)

# LIST ITEMS
class Items(ndb.Model):
    id = ndb.KeyProperty()
    item_initialProvider = ndb.StringProperty()
    item_name = ndb.StringProperty()
    item_asin = ndb.StringProperty(required=False)
    item_gbombID = ndb.StringProperty(required=False)
    item_metacriticPage = ndb.StringProperty(required=False)
    item_metascore = ndb.IntegerProperty(required=False)
    item_releasedate = ndb.DateProperty(required=False)
    item_platform = ndb.StringProperty(required=False)
    item_imageBaseURL = ndb.StringProperty(required=False)
    item_smallImage = ndb.StringProperty(required=False)
    item_thumbnailImage = ndb.StringProperty(required=False)
    item_largeImage = ndb.StringProperty(required=False)
    item_disqusID = ndb.IntegerProperty(required=False)

    item_date_added = ndb.DateTimeProperty(auto_now=False, auto_now_add=True)
    item_date_last_modfied = ndb.DateTimeProperty(auto_now=True, auto_now_add=True)

# ITEMS to TAGS to USERS link table
class ItemTagUser(ndb.Model):
    id = ndb.KeyProperty()
    user = ndb.KeyProperty(kind=Users)
    tag = ndb.KeyProperty(kind=Tags)
    item = ndb.KeyProperty(kind=Items)
    item_note = ndb.TextProperty(required=False)
    item_gameStatus = ndb.StringProperty(required=False)
    item_playStatus = ndb.StringProperty(required=False)
    item_userRating = ndb.StringProperty(required=False)

    item_date_added = ndb.DateTimeProperty(auto_now=False, auto_now_add=True)
    item_date_last_modfied = ndb.DateTimeProperty(auto_now=True, auto_now_add=True)



