from django.http import HttpResponse

import urllib2


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GAMESTATS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def gameStatsListByGPM(request):

    if 'platform' in request.GET:
        platform = request.GET.get('platform')

    # http://www.gamestats.com/index/gpm/xbox-360.html
    url = 'http://www.gamestats.com/index/gpm/' + platform + '.html'
    req = urllib2.Request(url)
    f = urllib2.urlopen(req)

    return HttpResponse(f.read(), mimetype='text/html')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IGN
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def ignUpcomingList(request):

    if 'platform' in request.GET:
        platform = request.GET.get('platform')

    # http://pc.ign.com/index/upcoming.html
    url = 'http://' + platform + '.ign.com/index/upcoming.html'
    req = urllib2.Request(url)
    f = urllib2.urlopen(req)

    return HttpResponse(f.read(), mimetype='text/html')
