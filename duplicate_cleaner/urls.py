from django.conf.urls import url
from duplicate_cleaner.views import IndexView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name="index"),
]
