from google.appengine.api import memcache

from tmz.models import ApiKeys

import logging


class Keys(object):

    # setKey
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def setKey(keyName, keyValue):

        # get existing key
        try:
            apiKey = ApiKeys.objects.get(keyName=keyName)
        except ApiKeys.DoesNotExist:
            apiKey = None

        # update existing keyName
        if apiKey:
            apiKey.keyName = keyName
            apiKey.keyValue = keyValue

        # create new key
        else:
            apiKey = ApiKeys(
                keyName=keyName,
                keyValue=keyValue
            )

        apiKey.save()

        # save to memcache
        if not memcache.add(keyName, keyValue):

            # update memcache
            memcache.set(key=keyName, value=keyValue)

        return 'keyName=%s keyValue=%s' % (keyName, keyValue)

    # getKey
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def getKey(keyName):

        # find key in memcache
        apiKey = memcache.get(keyName)

        # key not found in memcache
        if not apiKey:

            # fetch from ApiKeys table
            try:
                apiKeyRecord = ApiKeys.objects.get(keyName=keyName)
                # save to memcache
                if not memcache.add(apiKeyRecord.keyName, apiKeyRecord.keyValue):
                    logging.error('memcache set failed')

                apiKey = apiKeyRecord.keyValue

            except ApiKeys.DoesNotExist:
                apiKey = None

        return str(apiKey)
