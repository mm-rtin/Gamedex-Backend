from django.db import models


# API KEYS
class ApiKeys(models.Model):
    keyName = models.CharField(max_length=1024)
    keyValue = models.CharField(max_length=1024)

    class Meta:
        verbose_name_plural = 'ApiKeys'


# USERS
class Users(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    user_name = models.CharField(max_length=128, blank=True, null=True)
    user_password = models.CharField(max_length=128)
    user_email = models.CharField(max_length=256)
    user_secret_key = models.CharField(max_length=256)
    user_reset_code = models.CharField(max_length=256, blank=True, null=True)
    user_update_timestamp = models.CharField(max_length=32, blank=True, null=True)

    user_account_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    user_account_last_login = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Users'


# TAGS
class Tags(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    user = models.ForeignKey('Users')
    list_name = models.CharField(max_length=128)

    list_date_added = models.DateTimeField(auto_now=False, auto_now_add=True)
    list_date_last_modfied = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Lists'


# ITEMS to TAGS to USERS link table
class ItemTagUser(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    user = models.ForeignKey('Users')
    tag = models.ForeignKey('Tags')
    item = models.ForeignKey('Items')
    item_note = models.TextField(blank=True, null=True)
    item_gameStatus = models.CharField(max_length=16, blank=True, null=True)
    item_playStatus = models.CharField(max_length=16, blank=True, null=True)
    item_userRating = models.CharField(max_length=3, blank=True, null=True)

    item_date_added = models.DateTimeField(auto_now=False, auto_now_add=True)
    item_date_last_modfied = models.DateTimeField(auto_now=True, auto_now_add=True)


# LIST ITEMS
class Items(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    item_initialProvider = models.CharField(max_length=32)
    item_name = models.CharField(max_length=128)
    item_asin = models.CharField(max_length=16, blank=True, null=True)
    item_gbombID = models.CharField(max_length=16, blank=True, null=True)
    item_metacriticPage = models.CharField(max_length=512, blank=True, null=True)
    item_metascore = models.SmallIntegerField(max_length=3, blank=True, null=True)
    item_releasedate = models.DateField(blank=True, null=True)
    item_platform = models.CharField(max_length=32, blank=True, null=True)
    item_imageBaseURL = models.CharField(max_length=512, blank=True, null=True)
    item_smallImage = models.CharField(max_length=512, blank=True, null=True)
    item_thumbnailImage = models.CharField(max_length=512, blank=True, null=True)
    item_largeImage = models.CharField(max_length=512, blank=True, null=True)
    item_disqusID = models.SmallIntegerField(max_length=10, blank=True, null=True)

    item_date_added = models.DateTimeField(auto_now=False, auto_now_add=True)
    item_date_last_modfied = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        verbose_name_plural = 'ListItems'
