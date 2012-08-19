from django.conf.urls.defaults import patterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    # index
    (r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),

    # amazon product api rest proxy
    (r'^amazon/search/$', 'tmz.searchAPI.searchAmazon'),
    (r'^amazon/detail/$', 'tmz.searchAPI.detailAmazon'),

    # giantbomt api proxy
    (r'^giantbomb/search/$', 'tmz.searchAPI.searchGiantBomb'),
    (r'^giantbomb/detail/$', 'tmz.searchAPI.detailGiantBomb'),

    # metacritic datasource
    (r'^metacritic/search/$', 'tmz.searchAPI.searchMetacritic'),
    (r'^metacritic/cache/$', 'tmz.searchAPI.cacheMetacritic'),

    # gametrailers datasource
    (r'^gametrailers/search/$', 'tmz.searchAPI.searchGametrailers'),
    (r'^gametrailers/cache/$', 'tmz.searchAPI.cacheGametrailers'),

    # lists
    (r'^list/popular/$', 'tmz.listSources.popularList'),
    (r'^list/released/$', 'tmz.listSources.releasedList'),
    (r'^list/upcoming/$', 'tmz.listSources.upcomingList'),


    # gamedex rest api

    # user
    (r'^user/login/$', 'tmz.tmzAPI.login'),
    (r'^user/logout/$', 'tmz.tmzAPI.logout'),

    (r'^user/$', 'tmz.tmzAPI.user'),
    (r'^user/create/$', 'tmz.tmzAPI.createUser'),
    (r'^user/update/$', 'tmz.tmzAPI.updateUser'),
    (r'^user/resetcode/send/$', 'tmz.tmzAPI.sendResetCode'),
    (r'^user/resetcode/submit/$', 'tmz.tmzAPI.submitResetCode'),
    (r'^user/password/update/$', 'tmz.tmzAPI.updatePassword'),

    # tags
    (r'^tag/$', 'tmz.tmzAPI.getList'),
    (r'^tag/add/$', 'tmz.tmzAPI.createList'),
    (r'^tag/update/$', 'tmz.tmzAPI.updateList'),
    (r'^tag/delete/$', 'tmz.tmzAPI.deleteList'),

    # items
    (r'^item/$', 'tmz.tmzAPI.getListItems'),
    (r'^item/directory/$', 'tmz.tmzAPI.getDirectory'),
    (r'^item/tags/$', 'tmz.tmzAPI.getItemTags'),
    (r'^item/user/update/$', 'tmz.tmzAPI.updateUserItem'),
    (r'^item/shared/update/$', 'tmz.tmzAPI.updateSharedItem'),
    (r'^item/metacritic/update/$', 'tmz.tmzAPI.updateMetacritic'),
    (r'^item/add/$', 'tmz.tmzAPI.createListItem'),
    (r'^item/delete/$', 'tmz.tmzAPI.deleteListItem'),
    (r'^item/delete/batch/$', 'tmz.tmzAPI.deleteListItemsInBatch'),

    # data management
    (r'^manage/metascore/update$', 'tmz.dataManager.updateMetascore'),

    # management
    (r'^key/create$', 'tmz.management.setAPIKey'),
    (r'^copy/assets/$', 'tmz.management.copyAssetsToS3'),
    (r'^gamewallpapers/$', 'tmz.management.gamewallpapers'),

    (r'^createDisqusCategory/$', 'tmz.tmzAPI.createDisqusCategory'),

    # catch all
    (r'^.*/$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),


)
