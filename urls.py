from django.conf.urls.defaults import patterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    # index
    (r'^$', 'gamedex.views.index'),

    # amazon product api rest proxy
    (r'^amazon/search/$', 'gamedex.searchAPI.searchAmazon'),
    (r'^amazon/detail/$', 'gamedex.searchAPI.detailAmazon'),

    # giantbomt api proxy
    (r'^giantbomb/search/$', 'gamedex.searchAPI.searchGiantBomb'),
    (r'^giantbomb/detail/$', 'gamedex.searchAPI.detailGiantBomb'),

    # metacritic datasource
    (r'^metacritic/search/$', 'gamedex.searchAPI.searchMetacritic'),
    (r'^metacritic/cache/$', 'gamedex.searchAPI.cacheMetacritic'),

    # gametrailers datasource
    (r'^gametrailers/search/$', 'gamedex.searchAPI.searchGametrailers'),
    (r'^gametrailers/cache/$', 'gamedex.searchAPI.cacheGametrailers'),

    # steam datasource
    (r'^steam/search/$', 'gamedex.searchAPI.searchSteam'),
    (r'^steam/cache/$', 'gamedex.searchAPI.cacheSteam'),

    # lists
    (r'^list/popular/$', 'gamedex.listSources.popularList'),
    (r'^list/released/$', 'gamedex.listSources.releasedList'),
    (r'^list/upcoming/$', 'gamedex.listSources.upcomingList'),


    # gamedex rest api

    # user
    (r'^user/login/$', 'gamedex.gamedexAPI.login'),
    (r'^user/logout/$', 'gamedex.gamedexAPI.logout'),

    (r'^user/$', 'gamedex.gamedexAPI.user'),
    (r'^user/create/$', 'gamedex.gamedexAPI.createUser'),
    (r'^user/update/$', 'gamedex.gamedexAPI.updateUser'),
    (r'^user/delete/$', 'gamedex.gamedexAPI.deleteUser'),
    (r'^user/resetcode/send/$', 'gamedex.gamedexAPI.sendResetCode'),
    (r'^user/resetcode/submit/$', 'gamedex.gamedexAPI.submitResetCode'),
    (r'^user/password/update/$', 'gamedex.gamedexAPI.updatePassword'),

    # tags
    (r'^tag/$', 'gamedex.gamedexAPI.getList'),
    (r'^tag/add/$', 'gamedex.gamedexAPI.createList'),
    (r'^tag/update/$', 'gamedex.gamedexAPI.updateList'),
    (r'^tag/delete/$', 'gamedex.gamedexAPI.deleteList'),

    # items
    (r'^item/$', 'gamedex.gamedexAPI.getListItems'),
    (r'^item/directory/$', 'gamedex.gamedexAPI.getDirectory'),
    (r'^item/tags/$', 'gamedex.gamedexAPI.getItemTags'),
    (r'^item/user/update/$', 'gamedex.gamedexAPI.updateUserItem'),
    (r'^item/shared/price/update/$', 'gamedex.gamedexAPI.updateSharedItemPrice'),
    (r'^item/metacritic/update/$', 'gamedex.gamedexAPI.updateMetacritic'),
    (r'^item/add/$', 'gamedex.gamedexAPI.createListItem'),
    (r'^item/delete/$', 'gamedex.gamedexAPI.deleteListItem'),
    (r'^item/delete/batch/$', 'gamedex.gamedexAPI.deleteListItemsInBatch'),

    # import games
    (r'^import/$', 'gamedex.gamedexAPI.importGames'),

    # game sources
    (r'^steam/games/$', 'gamedex.gameSources.getSteamGames'),
    (r'^psn/games/$', 'gamedex.gameSources.getPSNGames_endpoint'),
    (r'^xbl/games/$', 'gamedex.gameSources.getXBLGames'),


    # data management

    # update metascore
    (r'^manage/metascore/update/$', 'gamedex.dataManager.updateMetascore'),

    # update steam
    (r'^manage/steam/price/update/$', 'gamedex.dataManager.updateSteamPrice'),
    (r'^manage/steam/page/update/$', 'gamedex.dataManager.updateSteamPage'),


    # management
    (r'^key/create/$', 'gamedex.management.setAPIKey'),
    (r'^copy/assets/$', 'gamedex.management.copyAssetsToS3'),
    (r'^gamewallpapers/$', 'gamedex.management.gamewallpapers'),

    (r'^createDisqusCategory/$', 'gamedex.gamedexAPI.createDisqusCategory'),

    # catch all
    (r'^.*/$', 'gamedex.views.index'),


)
