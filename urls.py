from django.conf.urls.defaults import patterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'T_MinusZero.views.home', name='home'),
    # url(r'^T_MinusZero/', include('T_MinusZero.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    # index
    (r'^$', 'tmz.views.index'),

    # amazon product api rest proxy
    (r'^amazon/search/$', 'tmz.searchAPI.searchAmazon'),
    (r'^amazon/detail/$', 'tmz.searchAPI.detailAmazon'),

    # giantbomt api proxy
    (r'^giantbomb/search/$', 'tmz.searchAPI.searchGiantBomb'),
    (r'^giantbomb/detail/$', 'tmz.searchAPI.detailGiantBomb'),

    # metacritic datasource
    (r'^metacritic/search/$', 'tmz.searchAPI.searchMetacritic'),
    (r'^metacritic/cache/$', 'tmz.searchAPI.cacheMetacritic'),

    # gamestats datasource
    (r'^popularlist/$', 'tmz.listSources.popularList'),

    # ign datasource
    (r'^upcominglist/$', 'tmz.listSources.upcomingList'),


    # t_minuszero rest api

    # user
    (r'^login/$', 'tmz.tmzAPI.login'),
    (r'^createuser/$', 'tmz.tmzAPI.createUser'),
    (r'^updateuser/$', 'tmz.tmzAPI.updateUser'),
    (r'^sendresetcode/$', 'tmz.tmzAPI.sendResetCode'),
    (r'^submitresetcode/$', 'tmz.tmzAPI.submitResetCode'),
    (r'^updatepassword/$', 'tmz.tmzAPI.updatePassword'),

    # tags
    (r'^tag/$', 'tmz.tmzAPI.getList'),
    (r'^tag/add/$', 'tmz.tmzAPI.createList'),
    (r'^tag/update/$', 'tmz.tmzAPI.updateList'),
    (r'^tag/delete/$', 'tmz.tmzAPI.deleteList'),

    # items
    (r'^item/$', 'tmz.tmzAPI.getListItems'),
    (r'^item/directory/$', 'tmz.tmzAPI.getDirectory'),
    (r'^item/tags/$', 'tmz.tmzAPI.getItemTags'),
    (r'^item/update/$', 'tmz.tmzAPI.updateItem'),
    (r'^item/update/metacritic/$', 'tmz.tmzAPI.updateMetacritic'),
    (r'^item/add/$', 'tmz.tmzAPI.createListItem'),
    (r'^item/delete/$', 'tmz.tmzAPI.deleteListItem'),
    (r'^item/delete/batch$', 'tmz.tmzAPI.deleteListItemsInBatch'),


    (r'^gamewallpapers/$', 'tmz.listSources.gamewallpapers'),
)
