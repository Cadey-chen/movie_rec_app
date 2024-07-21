from django.shortcuts import render
from django.http import HttpResponse
import os 
from .models import Movie
from .recommender import movies_by_genre, find_matches, user_defined_recommender, process_sim_titles
from .process_images import fetch_images
from .forms import GenreForm

# custom genres, keywords, and description inputs for a historical romance movie
# in the English countryside to test the user defined recommender
genres = ["Drama", "Romance", "Family", "History"]
keywords = ["Love", "Family", "Aristocracy", "England", "Lovers", "Fate", "Sadness", "Duty", "Period", "Historical"]
overview = "Set in the English countryside, this is a love story in the midst of a declining aristocratic family in the 18th century. Faye, deeply in love with her childhood sweetheart Dustin, must make the choice between duty to her family and following her heart."

# dummy movie data 
romance_movies = []

# img_root_path = os.path.join(os.path.dirname(__file__), "templates", "movies", "posters")
# movies_by_genre("Adventure", "ratings", 10)
# find_matches("The Matrix", 10)

# query_movies queries movie objects from the database
def query_movies(movie_ids):
    # fetch images for movie_ids first
    fetch_images(movie_ids)
    result = []
    # fetch movies from db by id
    for movie_id in movie_ids:
        cur_movie = Movie.objects.get(movie_id=movie_id)
        result.append(cur_movie)
    return result 

# get_movies_by_genre gets the movie metadata and downloads 
# images from the TMDB database 
def get_movies_by_genre(genre, rank_type, num_movies):
    movie_ids = movies_by_genre(genre, rank_type, num_movies)
    result = query_movies(movie_ids)
    return result 

# home view 
def home(request):
    return render(request, "movies/home.html", {"title": "Movies Home"})

# movies_by_genre view
def movies_by_genre_view(request):
    if request.method == "POST":
        genre_form = GenreForm(request.POST)
        if genre_form.is_valid():
            genre_choice = genre_form.cleaned_data['genre']
            rank_choice = genre_form.cleaned_data['rank_type']
            num_choice = int(genre_form.cleaned_data['num_movies'])
            # find those movies 
            movies_list = get_movies_by_genre(genre_choice, rank_choice, num_choice)
            context = {
                "movies": movies_list,
                "title": "Top {num_str} {genre_str} movies".format(num_str=num_choice, genre_str=genre_choice)
            }
            return render(request, "movies/movies_by_genre.html", context)
    else:
        genre_form = GenreForm()
        context = {
            "title": "Selection Page",
            "form": genre_form
        }
        return render(request, "movies/genre_form.html", context)
    
# movies by similarity view 
def movies_by_similarity(request):
    context = {}
    if "movie_name" in request.GET:
        movie_name = request.GET["movie_name"]
        results = process_sim_titles(movie_name)
        print(results)
        context["search_results"] = results
    return render(request, "movies/movies_by_similarity.html", context)

# about view
def about(request):
    return render(request, "movies/about.html", {"title": "About Page"})