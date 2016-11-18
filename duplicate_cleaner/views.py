import spotipy
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext

from django.views.generic.base import TemplateView, RedirectView


class IndexView(TemplateView):
    template_name = "duplicate_cleaner/index.html"


class HomeView(TemplateView):
    template_name = "duplicate_cleaner/home.html"


class SpotifyMixin(object):

    def get(self, request, **kwargs):
        try:
            return super(SpotifyMixin, self).get(request, **kwargs)
        except spotipy.SpotifyException, e:
            messages.warning(request, ugettext(u"The Access Token expired."))
            return redirect("%s?next=/" % reverse("auth:logout"))

    def get_tracks(self, request, playlist_id, offset=0):
        social_auth = request.user.social_auth.first()
        sp = spotipy.Spotify(auth=social_auth.access_token)
        data = sp.user_playlist_tracks(request.user.username, playlist_id, offset=offset)
        items = data.get("items")
        if data.get("next"):
            offset = data.get("offset") + data.get("limit")
            return self.get_tracks(playlist_id, offset=offset) + items
        return items

    def get_playlists(self, request, offset=0):
        social_auth = request.user.social_auth.first()
        sp = spotipy.Spotify(auth=social_auth.access_token)
        data = sp.user_playlists(request.user.username, offset=offset)
        items = data.get("items")
        if data.get("next"):
            offset = data.get("offset") + data.get("limit")
            return self.get_playlists(offset=offset) + items
        return items


class PlayListView(SpotifyMixin, TemplateView):
    template_name = "duplicate_cleaner/playlist.html"

    def get_context_data(self, **kwargs):
        context = super(PlayListView, self).get_context_data(**kwargs)
        playlists = self.get_playlists(self.request)
        for playlist in playlists:
            if playlist["owner"]["id"] != self.request.user.username:
                continue
            tracks = self.get_tracks(self.request, playlist_id=playlist["id"])
            track_ids = map(lambda x: x["track"]["id"], tracks)
            duplicate_track_ids = list(set(filter(lambda x: track_ids.count(x) > 1, track_ids)))
            playlist["duplicate_count"] = len(duplicate_track_ids)
        context["playlists"] = playlists
        return context


class PlayListDetailView(SpotifyMixin, TemplateView):
    template_name = "duplicate_cleaner/playlist_detail.html"

    def get_context_data(self, **kwargs):
        context = super(PlayListDetailView, self).get_context_data(**kwargs)
        playlist_id = kwargs.get("playlist_id")
        context["tracks"] = self.get_tracks(self.request, playlist_id)
        return context


class DuplicateCleanerView(SpotifyMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse("playlist-detail", kwargs={"playlist_id": kwargs.get("playlist_id")})

    def get(self, request, *args, **kwargs):
        try:
            playlist_id = kwargs.get("playlist_id")
            social_auth = request.user.social_auth.first()
            sp = spotipy.Spotify(auth=social_auth.access_token)
            tracks = self.get_tracks(request, playlist_id=playlist_id)
            track_ids = map(lambda x: x["track"]["id"], tracks)
            duplicate_track_ids = list(set(filter(lambda x: track_ids.count(x) > 1, track_ids)))
            if duplicate_track_ids:
                sp.user_playlist_remove_all_occurrences_of_tracks(
                    request.user.username, playlist_id, duplicate_track_ids
                )
                sp.user_playlist_add_tracks(request.user.username, playlist_id, duplicate_track_ids)
                messages.success(request, ugettext(u"Duplicate Tracks Removed Successfully."))
            return super(DuplicateCleanerView, self).get(request, **kwargs)
        except spotipy.SpotifyException, e:
            messages.warning(request, ugettext(u"The Access Token expired."))
            return redirect("%s?next=/" % reverse("auth:logout"))
