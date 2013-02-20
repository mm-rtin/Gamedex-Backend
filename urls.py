from django.conf.urls.defaults import patterns


urlpatterns = patterns('',

    # index
    (r'^$', 'gamedex.views.index'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # third party proxies
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # amazon source
    (r'^amazon/search/$',       'gamedex.api.search.searchAmazon'),
    (r'^amazon/detail/$',       'gamedex.api.search.detailAmazon'),

    (r'^giantbomb/search/$',    'gamedex.api.search.searchGiantBomb'),
    (r'^giantbomb/detail/$',    'gamedex.api.search.detailGiantBomb'),
    (r'^giantbomb/video/$',    'gamedex.api.search.videoGiantBomb'),

    (r'^metacritic/search/$',   'gamedex.api.search.searchMetacritic'),
    (r'^metacritic/cache/$',    'gamedex.api.search.cacheMetacritic'),

    (r'^gametrailers/search/$', 'gamedex.api.search.searchGametrailers'),
    (r'^gametrailers/cache/$',  'gamedex.api.search.cacheGametrailers'),

    (r'^steam/search/$',        'gamedex.api.search.searchSteam'),
    (r'^steam/cache/$',         'gamedex.api.search.cacheSteam'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # list sources
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    (r'^list/popular/$',                'gamedex.api.list.popularList'),
    (r'^list/ign/upcoming/popular/$',    'gamedex.api.list.ignUpcomingPopularList'),
    (r'^list/ign/upcoming/$',           'gamedex.api.list.ignUpcomingList'),
    (r'^list/ign/reviewed/$',           'gamedex.api.list.ignReviewedList'),
    (r'^list/gt/released/$',            'gamedex.api.list.gtReleasedList'),


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # gamedex rest api
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # user
    (r'^user/login/$',                  'gamedex.api.gamedex.login'),
    (r'^user/logout/$',                 'gamedex.api.gamedex.logout'),
    (r'^user/$',                        'gamedex.api.gamedex.user'),
    (r'^user/create/$',                 'gamedex.api.gamedex.createUser'),
    (r'^user/update/$',                 'gamedex.api.gamedex.updateUser'),
    (r'^user/delete/$',                 'gamedex.api.gamedex.deleteUser'),
    (r'^user/resetcode/send/$',         'gamedex.api.gamedex.sendResetCode'),
    (r'^user/resetcode/submit/$',       'gamedex.api.gamedex.submitResetCode'),
    (r'^user/password/update/$',        'gamedex.api.gamedex.updatePassword'),

    # tag
    (r'^tag/$',                         'gamedex.api.gamedex.getTag'),
    (r'^tag/add/$',                     'gamedex.api.gamedex.createTag'),
    (r'^tag/update/$',                  'gamedex.api.gamedex.updateTag'),
    (r'^tag/delete/$',                  'gamedex.api.gamedex.deleteTag'),

    # item
    (r'^item/$',                        'gamedex.api.gamedex.getTagItems'),
    (r'^item/directory/$',              'gamedex.api.gamedex.getDirectory'),
    (r'^item/tags/$',                   'gamedex.api.gamedex.getItemTags'),
    (r'^item/user/update/$',            'gamedex.api.gamedex.updateUserItem'),
    (r'^item/shared/price/update/$',    'gamedex.api.gamedex.updateSharedItemPrice'),
    (r'^item/metacritic/update/$',      'gamedex.api.gamedex.updateMetacritic'),
    (r'^item/add/$',                    'gamedex.api.gamedex.createTagItem'),
    (r'^item/delete/$',                 'gamedex.api.gamedex.deleteTagItem'),
    (r'^item/delete/batch/$',           'gamedex.api.gamedex.deleteTagItemsInBatch'),

    # import games
    (r'^import/$', 'gamedex.api.gamedex.importGames'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # data management
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # update metascore
    (r'^manage/metascore/update/$',     'gamedex.management.dataManager.updateMetascore'),
    # update steam
    (r'^manage/steam/price/update/$',   'gamedex.management.dataManager.updateSteamPrice'),
    (r'^manage/steam/page/update/$',    'gamedex.management.dataManager.updateSteamPage'),

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # admin
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    (r'^key/create/$',              'gamedex.management.management.setAPIKey'),
    (r'^copy/assets/$',             'gamedex.management.management.copyAssetsToS3'),
    (r'^gamewallpapers/$',          'gamedex.management.management.gamewallpapers'),

    (r'^createDisqusCategory/$',    'gamedex.gamedexAPI.createDisqusCategory'),

    # catch all
    (r'^.*/$', 'gamedex.views.index'),


)
