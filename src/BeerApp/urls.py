from django.conf.urls import patterns, include, url
from django.contrib import admin

from BeerNav.views import BeerView, BeerListView, HomePageView, PollView


urlpatterns = patterns('',
                       url(r'(^$|^index.html$)', HomePageView.as_view()),
                       url(r'^beers/', BeerListView.as_view()),
                       url(r'^beer/(?P<pk>\d+)', BeerView.as_view()),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^poll/', PollView.as_view()),
)
