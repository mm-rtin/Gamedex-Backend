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
    (r'^itemsearch/amazon/(?P<searchIndex>\w*)/(?P<browseNode>\d*)/(?P<keywords>[\w\+!@#$%^&*-?.,\s]+)/(?P<responseGroup>[\w,]*)/(?P<page>\d*)$', 'tmz.views.itemSearchAmazon'),
    (r'^itemlookup_asin/(?P<asin>\w+)/(?P<responseGroup>[\w,]*)$', 'tmz.views.itemLookupASIN'),

    # giantbomt api proxy
    (r'^itemsearch/giantbomb/(?P<keywords>[\w\+!@#$%^&*-?.,\s]+)/(?P<page>\d*)$', 'tmz.views.itemSearchGiantBomb'),


    # t_minuszero rest api

    # user
    (r'^login/$', 'tmz.views.login'),
    (r'^createuser/$', 'tmz.views.createUser'),

    # tags
    (r'^list/$', 'tmz.views.getList'),
    (r'^list/add$', 'tmz.views.createList'),
    (r'^list/delete$', 'tmz.views.deleteList'),

    # items
    (r'^item/$', 'tmz.views.getListItems'),
    (r'^item/directory$', 'tmz.views.getDirectory'),
    (r'^item/tags$', 'tmz.views.getItemTags'),
    (r'^item/add$', 'tmz.views.createListItem'),
    (r'^item/delete$', 'tmz.views.deleteListItem'),
    (r'^item/batch-delete$', 'tmz.views.deleteListItemsInBatch'),
)
