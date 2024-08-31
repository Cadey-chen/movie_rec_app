from django.db import models
from django.utils import timezone 
        
class Movie(models.Model):
    genres = [
        ("Action", "Action"),
        ("Adventure", "Adventure"),
        ("Animation", "Animation"),
        ("Comedy", "Comedy"),
        ("Crime", "Crime"),
        ("Documentary", "Documentary"),
        ("Drama", "Drama"),
        ("Family", "Family"),
        ("Fantasy", "Fantasy"),
        ("History", "History"),
        ("Mystery", "Mystery"),
        ("Romance", "Romance"),
        ("Science Fiction", "Science Fiction"),
        ("Thriller", "Thriller"),
        ("Western", "Western"),
    ]

    movie_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    desc = models.TextField(max_length=1000)
    genre = models.TextField(max_length=1000, choices=genres)
    release_date = models.DateField()
    vote_count = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    img = models.ImageField(default=None, upload_to="posters/", null=True)

    def __str__(self):
        return self.title
    
    """
    movie_obj = {
            "Title": self.title,
            "Release Date": self.release_date,
            "Genre": self.genre,
            "Rating": self.rating,
            "Vote Count": self.vote_count,
            "Description": self.desc,
        }
    """
