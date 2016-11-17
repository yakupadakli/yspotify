from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from duplicate_cleaner.views import IndexView, HomeView, PlayListView, PlayListDetailView
from yspotify.decorators import anonymous_required

urlpatterns = [
    url(r'^$', anonymous_required(IndexView.as_view()), name="index"),
    url(r'^home/$', login_required(HomeView.as_view()), name="home"),
    url(r'^home/playlist/$', login_required(PlayListView.as_view()), name="playlists"),
    url(r'^home/playlist/(?P<playlist_id>[^/]+)/$',
        login_required(PlayListDetailView.as_view()), name="playlist-detail"),
]
