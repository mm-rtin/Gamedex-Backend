from django.db import models


# USERS
class Users(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    user_login = models.CharField(max_length=128)
    user_password = models.CharField(max_length=128)
    user_email = models.CharField(max_length=256)
    user_secret_key = models.CharField(max_length=256)

    class Meta:
        verbose_name_plural = 'Users'


# TAGS
class Tags(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    user = models.ForeignKey('Users')
    list_name = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = 'Lists'


# ITEMS to TAGS to USERS link table
class ItemTagUser(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    user = models.ForeignKey('Users')
    tag = models.ForeignKey('Tags')
    item = models.ForeignKey('Items')
    item_note = models.TextField(blank=True)


# LIST ITEMS
class Items(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    user = models.ForeignKey('Users')
    item_initialProvider = models.CharField(max_length=32)
    item_asin = models.CharField(max_length=16, blank=True)
    item_gbombID = models.CharField(max_length=16, blank=True)
    item_metacriticPage = models.CharField(max_length=512, blank=True)
    item_metascore = models.SmallIntegerField(max_length=3, blank=True)
    item_name = models.CharField(max_length=128)
    item_releasedate = models.DateField(blank=True)
    item_platform = models.CharField(max_length=32, blank=True)
    item_smallImage = models.CharField(max_length=512, blank=True)
    item_thumbnailImage = models.CharField(max_length=512, blank=True)
    item_largeImage = models.CharField(max_length=512, blank=True)
    item_gameStatus = models.CharField(max_length=16)
    item_playStatus = models.CharField(max_length=16)
    item_userRating = models.CharField(max_length=3)

    class Meta:
        verbose_name_plural = 'ListItems'
