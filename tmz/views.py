from django.shortcuts import render_to_response
import random


# index page
def index(request):
    return render_to_response('index.html', {'random': random.random()})
