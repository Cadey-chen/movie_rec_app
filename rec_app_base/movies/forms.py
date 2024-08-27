from django import forms 
from .models import Movie

GENRES = [
    (None, "Select Genre"),
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
    (None, "Ranking Type"),
    ("ratings", "Ratings"),
    ("popularity", "Popularity"),
    ("bayesian", "Bayesian"),
]

NUM_MOVIES = [
    (None, "Number Movies"),
    ("10", "10"),
    ("20", "20"),
    ("50", "50"),
]

class GenreForm(forms.Form):
    genre = forms.ChoiceField(choices=GENRES, label='Genre', widget=forms.Select(attrs={'class': 'dropdown show'}))
    rank_type = forms.ChoiceField(choices=RANK_TYPES, label="Rank by", widget=forms.Select(attrs={'class': 'form-control dropdown-toggle'}))
    num_movies = forms.ChoiceField(choices=NUM_MOVIES, label='Number of Movies', widget=forms.Select(attrs={'class': 'form-control'}))