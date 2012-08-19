from django.shortcuts import render_to_response


# index page
def index(request):
    return render_to_response('index.html')
