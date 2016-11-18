from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from duplicate_cleaner.views import IndexView, HomeView, PlayListView, PlayListDetailView, DuplicateCleanerView
from yspotify.decorators import anonymous_required

urlpatterns = [
    url(r'^$', anonymous_required(IndexView.as_view()), name="index"),
    url(r'^home/$', login_required(PlayListView.as_view()), name="playlists"),
    url(r'^playlist/$', login_required(PlayListView.as_view()), name="playlists1"),
    url(r'^playlist/(?P<playlist_id>[^/]+)/$',
        login_required(PlayListDetailView.as_view()), name="playlist-detail"),
    url(r'^clean/duplicate/(?P<playlist_id>[^/]+)/$',
        login_required(DuplicateCleanerView.as_view()), name="clean-duplicate"),
]
