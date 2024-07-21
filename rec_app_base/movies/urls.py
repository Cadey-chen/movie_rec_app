from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="movies-about"),
    path("movies_by_genre/", views.movies_by_genre_view, name="movies-by-genre"),
    path("movies_by_similarity/", views.movies_by_similarity, name="movies-by-similarity")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)