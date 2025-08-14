from django.urls import path
from . import views

app_name = "shortner"

urlpatterns = [
    path("", views.index, name="index"),
    path("stats/", views.stats, name="stats"),
    path("api/shorten/", views.api_shorten, name="api_shorten"),     
    path("<str:code>/", views.redirect_code, name="redirect"),       
]