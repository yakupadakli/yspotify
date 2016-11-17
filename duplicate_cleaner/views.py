import spotipy
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from django.views.generic.base import TemplateView


class IndexView(TemplateView):
    template_name = "duplicate_cleaner/index.html"


class HomeView(TemplateView):
    template_name = "duplicate_cleaner/home.html"


class SpotifyMixin(object):

    def get(self, request, **kwargs):
        try:
            return super(SpotifyMixin, self).get(request, **kwargs)
        except spotipy.SpotifyException, e:
            messages.warning(request, e)
            return redirect("%s?next=/" % reverse("auth:logout"))


class PlayListView(SpotifyMixin, TemplateView):
    template_name = "duplicate_cleaner/playlist.html"

    def get_context_data(self, **kwargs):
        context = super(PlayListView, self).get_context_data(**kwargs)
        context["playlists"] = self.get_playlists()
        return context

    def get_playlists(self, offset=0):
        social_auth = self.request.user.social_auth.first()
        sp = spotipy.Spotify(auth=social_auth.access_token)
        data = sp.user_playlists(self.request.user.username, limit=2, offset=offset)
        items = data.get("items")
        if data.get("next"):
            offset = data.get("offset") + data.get("limit")
            return self.get_playlists(offset=offset) + items
        return items


class PlayListDetailView(SpotifyMixin, TemplateView):
    template_name = "duplicate_cleaner/playlist_detail.html"

    def get_context_data(self, **kwargs):
        context = super(PlayListDetailView, self).get_context_data(**kwargs)
        playlist_id = kwargs.get("playlist_id")
        context["tracks"] = self.get_tracks(playlist_id)
        return context

    def get_tracks(self, playlist_id, offset=0):
        social_auth = self.request.user.social_auth.first()
        sp = spotipy.Spotify(auth=social_auth.access_token)
        data = sp.user_playlist_tracks(self.request.user.username, playlist_id, limit=2, offset=offset)
        items = data.get("items")
        if data.get("next"):
            offset = data.get("offset") + data.get("limit")
            return self.get_tracks(playlist_id, offset=offset) + items
        return items
