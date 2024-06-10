from django.shortcuts import render
from django.http import HttpResponse
import os 
from .models import Movie
from .recommender import movies_by_genre
from .process_images import fetch_images

# Create your views here.

# dummy movie data 
romance_movies = []

movie_ids = movies_by_genre("Romance", "ratings", 10)
print(movie_ids)

# fetch the movie poster from TMDB API
fetch_images(movie_ids)

img_root_path = os.path.join(os.path.dirname(__file__), "templates", "movies", "posters")

# fetch movies from db by id
for movie_id in movie_ids:
    cur_movie = Movie.objects.get(movie_id=movie_id)
    movie_obj = {
        "title": cur_movie.title,
        "release_date": cur_movie.release_date,
        "genre": cur_movie.genre,
        "rating": cur_movie.rating,
        "vote_count": cur_movie.vote_count,
        "desc": cur_movie.desc,
        "img_url": os.path.join(img_root_path, "poster_{movie_id}.jpeg".format(movie_id=cur_movie.movie_id))
    }
    romance_movies.append(movie_obj)

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