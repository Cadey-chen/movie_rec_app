from django import forms 
from .models import Movie

GENRES = [
    ("Action", "Action"),
    ("Adventure", "Adventure"),
    ("Comedy", "Comedy"),
    ("Crime", "Crime"),
    ("Documentary", "Documentary"),
    ("Drama", "Drama"),
    ("Family", "Family"),
    ("Fantasy", "Fantasy"),
    ("Romance", "Romance"),
    ("Science Fiction", "Science Fiction"),
    ("Western", "Western"),
]

RANK_TYPES = [
    ("ratings", "Ratings"),
    ("popularity", "Popularity"),
    ("bayesian", "Bayesian"),
]

NUM_MOVIES = [
    ("10", "10"),
    ("20", "20"),
    ("50", "50"),
]

class GenreForm(forms.Form):
    genre = forms.ChoiceField(choices=GENRES, label='Genre')
    rank_type = forms.ChoiceField(choices=RANK_TYPES, label="Rank by")
    num_movies = forms.ChoiceField(choices=NUM_MOVIES, label='Number of Movies')