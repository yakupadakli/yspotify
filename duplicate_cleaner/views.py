import spotipy

from django.views.generic.base import TemplateView


class IndexView(TemplateView):
    template_name = "duplicate_cleaner/index.html"


class HomeView(TemplateView):
    template_name = "duplicate_cleaner/home.html"


class PlayListView(TemplateView):
    template_name = "duplicate_cleaner/playlist.html"

    def get_context_data(self, **kwargs):
        context = super(PlayListView, self).get_context_data(**kwargs)
        social_auth = self.request.user.social_auth.first()
        sp = spotipy.Spotify(auth=social_auth.access_token)
        context["playlists"] = sp.user_playlists(self.request.user.username)
        return context


class PlayListDetailView(TemplateView):
    template_name = "duplicate_cleaner/playlist_detail.html"

    def get_context_data(self, **kwargs):
        context = super(PlayListDetailView, self).get_context_data(**kwargs)
        playlist_id = kwargs.get("playlist_id")
        context["tracks"] = self.get_tracks(playlist_id)
        return context

    def get_tracks(self, playlist_id):
        social_auth = self.request.user.social_auth.first()
        sp = spotipy.Spotify(auth=social_auth.access_token)
        data = sp.user_playlist_tracks(self.request.user.username, playlist_id)
        if data.get("next"):
            return self.get_tracks(playlist_id)
        return data.get("items")
