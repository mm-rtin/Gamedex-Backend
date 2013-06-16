import random
from django.shortcuts import render_to_response

# index page
def index(request):

    # random image color
    randomColorIndex = random.randrange(3) + 1

    # create context
    context = {'randomColorIndex': randomColorIndex}

    return render_to_response('index.html', context)
