from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from google.appengine.ext import ndb

from django.core import serializers


# database models
from tmz.models import Users, Items, Tags, ItemTagUser

# index page
def index(request):
    return render_to_response('index.html')


# GET DIRECTORY OF ID/3RD PARTY IDs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getDirectory(request):

    user = Users.query(Users.id == ndb.Key(Users, '1'), Users.user_secret_key == '1')

    data = serializers.serialize("json", user)

    return HttpResponse(data, mimetype='application/json')
