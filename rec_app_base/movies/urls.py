from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="movies-about"),
    path("movies_by_genre/", views.movies_by_genre_view, name="movies-by-genre"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)