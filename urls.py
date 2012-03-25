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
    (r'^itemsearch/amazon/$', 'tmz.searchAPI.itemSearchAmazon'),
    (r'^itemdetail/amazon/$', 'tmz.searchAPI.itemDetailAmazon'),

    # giantbomt api proxy
    (r'^itemsearch/giantbomb/$', 'tmz.searchAPI.itemSearchGiantBomb'),
    (r'^itemdetail/giantbomb/$', 'tmz.searchAPI.itemDetailGiantBomb'),

    # metacritic datasource
    (r'^itemsearch/metacritic/$', 'tmz.searchAPI.itemSearchMetacritic'),

    # gamestats datasource
    (r'^popularlist/gamestats/gpm$', 'tmz.listSources.gameStatsListByGPM'),

    # ign datasource
    (r'^upcominglist/ign$', 'tmz.listSources.ignUpcomingList'),


    # t_minuszero rest api

    # user
    (r'^login/$', 'tmz.tmzAPI.login'),
    (r'^createuser/$', 'tmz.tmzAPI.createUser'),

    # tags
    (r'^list/$', 'tmz.tmzAPI.getList'),
    (r'^list/add$', 'tmz.tmzAPI.createList'),
    (r'^list/delete$', 'tmz.tmzAPI.deleteList'),

    # items
    (r'^item/$', 'tmz.tmzAPI.getListItems'),
    (r'^item/directory$', 'tmz.tmzAPI.getDirectory'),
    (r'^item/tags$', 'tmz.tmzAPI.getItemTags'),
    (r'^item/update$', 'tmz.tmzAPI.updateItem'),
    (r'^item/add$', 'tmz.tmzAPI.createListItem'),
    (r'^item/delete$', 'tmz.tmzAPI.deleteListItem'),
    (r'^item/batch-delete$', 'tmz.tmzAPI.deleteListItemsInBatch'),
)
