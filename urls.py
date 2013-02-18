from django.conf.urls.defaults import patterns


urlpatterns = patterns('',

    # index
    (r'^$', 'gamedex.views.index'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # third party proxies
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # amazon source
    (r'^amazon/search/$',       'gamedex.searchAPI.searchAmazon'),
    (r'^amazon/detail/$',       'gamedex.searchAPI.detailAmazon'),

    (r'^giantbomb/search/$',    'gamedex.searchAPI.searchGiantBomb'),
    (r'^giantbomb/detail/$',    'gamedex.searchAPI.detailGiantBomb'),

    (r'^metacritic/search/$',   'gamedex.searchAPI.searchMetacritic'),
    (r'^metacritic/cache/$',    'gamedex.searchAPI.cacheMetacritic'),

    (r'^gametrailers/search/$', 'gamedex.searchAPI.searchGametrailers'),
    (r'^gametrailers/cache/$',  'gamedex.searchAPI.cacheGametrailers'),

    (r'^steam/search/$',        'gamedex.searchAPI.searchSteam'),
    (r'^steam/cache/$',         'gamedex.searchAPI.cacheSteam'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # list sources
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    (r'^list/popular/$',    'gamedex.listSources.popularList'),
    (r'^list/released/$',   'gamedex.listSources.releasedList'),
    (r'^list/upcoming/$',   'gamedex.listSources.upcomingList'),


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # gamedex rest api
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # user
    (r'^user/login/$',                  'gamedex.gamedexAPI.login'),
    (r'^user/logout/$',                 'gamedex.gamedexAPI.logout'),
    (r'^user/$',                        'gamedex.gamedexAPI.user'),
    (r'^user/create/$',                 'gamedex.gamedexAPI.createUser'),
    (r'^user/update/$',                 'gamedex.gamedexAPI.updateUser'),
    (r'^user/delete/$',                 'gamedex.gamedexAPI.deleteUser'),
    (r'^user/resetcode/send/$',         'gamedex.gamedexAPI.sendResetCode'),
    (r'^user/resetcode/submit/$',       'gamedex.gamedexAPI.submitResetCode'),
    (r'^user/password/update/$',        'gamedex.gamedexAPI.updatePassword'),

    # tag
    (r'^tag/$',                         'gamedex.gamedexAPI.getTag'),
    (r'^tag/add/$',                     'gamedex.gamedexAPI.createTag'),
    (r'^tag/update/$',                  'gamedex.gamedexAPI.updateTag'),
    (r'^tag/delete/$',                  'gamedex.gamedexAPI.deleteTag'),

    # item
    (r'^item/$',                        'gamedex.gamedexAPI.getTagItems'),
    (r'^item/directory/$',              'gamedex.gamedexAPI.getDirectory'),
    (r'^item/tags/$',                   'gamedex.gamedexAPI.getItemTags'),
    (r'^item/user/update/$',            'gamedex.gamedexAPI.updateUserItem'),
    (r'^item/shared/price/update/$',    'gamedex.gamedexAPI.updateSharedItemPrice'),
    (r'^item/metacritic/update/$',      'gamedex.gamedexAPI.updateMetacritic'),
    (r'^item/add/$',                    'gamedex.gamedexAPI.createTagItem'),
    (r'^item/delete/$',                 'gamedex.gamedexAPI.deleteTagItem'),
    (r'^item/delete/batch/$',           'gamedex.gamedexAPI.deleteTagItemsInBatch'),

    # import games
    (r'^import/$', 'gamedex.gamedexAPI.importGames'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # game imports
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    (r'^steam/games/$', 'gamedex.gameSources.getSteamGames'),
    (r'^psn/games/$',   'gamedex.gameSources.getPSNGames_endpoint'),
    (r'^xbl/games/$',   'gamedex.gameSources.getXBLGames'),


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # data management
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # update metascore
    (r'^manage/metascore/update/$',     'gamedex.dataManager.updateMetascore'),
    # update steam
    (r'^manage/steam/price/update/$',   'gamedex.dataManager.updateSteamPrice'),
    (r'^manage/steam/page/update/$',    'gamedex.dataManager.updateSteamPage'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # admin
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    (r'^key/create/$',              'gamedex.management.setAPIKey'),
    (r'^copy/assets/$',             'gamedex.management.copyAssetsToS3'),
    (r'^gamewallpapers/$',          'gamedex.management.gamewallpapers'),

    (r'^createDisqusCategory/$',    'gamedex.gamedexAPI.createDisqusCategory'),

    # catch all
    (r'^.*/$', 'gamedex.views.index'),


)
