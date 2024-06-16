from django.shortcuts import render
from django.http import HttpResponse
import os 
from .models import Movie
from .recommender import movies_by_genre
from .process_images import fetch_images

# Create your views here.

# dummy movie data 
romance_movies = []

movie_ids = movies_by_genre("Family", "bayesian", 10)
print(movie_ids)

# fetch the movie poster from TMDB API
fetch_images(movie_ids)

img_root_path = os.path.join(os.path.dirname(__file__), "templates", "movies", "posters")

# fetch movies from db by id
for movie_id in movie_ids:
    cur_movie = Movie.objects.get(movie_id=movie_id)
    print(cur_movie.img.url)
    romance_movies.append(cur_movie)

# home view
def home(request):
    context = {
        "movies": romance_movies,
        "title": "Romance movies"
    }
    return render(request, "movies/home.html", context)

# about view
def about(request):
    return render(request, "movies/about.html", {"title": "About Page"})