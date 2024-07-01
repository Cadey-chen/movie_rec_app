from django.shortcuts import render
from django.http import HttpResponse
import os 
from .models import Movie
from .recommender import movies_by_genre, find_matches, user_defined_recommender
from .process_images import fetch_images

# custom genres, keywords, and description inputs for a historical romance movie
# in the English countryside to test the user defined recommender
genres = ["Drama", "Romance", "Family", "History"]
keywords = ["Love", "Family", "Aristocracy", "England", "Lovers", "Fate", "Sadness", "Duty", "Period", "Historical"]
overview = "Set in the English countryside, this is a love story in the midst of a declining aristocratic family in the 18th century. Faye, deeply in love with her childhood sweetheart Dustin, must make the choice between duty to her family and following her heart."

# dummy movie data 
romance_movies = []

# movies_by_genre("Adventure", "ratings", 10)
# find_matches("The Matrix", 10)

movie_ids = user_defined_recommender(genres, keywords, overview, 10)
print(movie_ids)

# fetch the movie poster from TMDB API
fetch_images(movie_ids)

img_root_path = os.path.join(os.path.dirname(__file__), "templates", "movies", "posters")

# fetch movies from db by id
for movie_id in movie_ids:
    cur_movie = Movie.objects.get(movie_id=movie_id)
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