"""keys.py: Save and Retrieve keys from Datastore """

__author__ = "Michael Martin"
__status__ = "Production"

import logging

from google.appengine.api import memcache

from models import ApiKeys


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Keys
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Keys(object):

    # setKey
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def setKey(keyName, keyValue):

        # get existing key
        apiKey = ApiKeys.query(ApiKeys.keyName == keyName).get()

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

        apiKey.put()

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
            apiKeyRecord = ApiKeys.query(ApiKeys.keyName == keyName).get()

            if apiKeyRecord:
                # save to memcache
                if not memcache.add(apiKeyRecord.keyName, apiKeyRecord.keyValue):
                    logging.error('memcache set failed')

            apiKey = apiKeyRecord.keyValue

        return str(apiKey)
