import requests
import json, operator
import os
from bs4 import BeautifulSoup
from .models import Movie
from concurrent.futures import ThreadPoolExecutor
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.core.files.base import ContentFile
from .config.tmdb_config import headers

# fetch a movie poster image from TMDB and save the image
# to the local database

CONFIG_URL = "https://api.themoviedb.org/3/configuration"
IMAGES_BASE_URL = "https://api.themoviedb.org/3/movie/{movie_id}/images"

def get_response(url):
    """
    Sends a request to the API and format the response in json format
    """
    response = requests.get(url, headers=headers)
    res_json = response.json()
    return res_json


def save_poster(movie_id, movie_obj, img_url):
    """
    save the movie poster file to the local file system 
    """
    res = requests.get(img_url)
    img_suffix = res.headers['content-type'].split('/')[-1]
    img_name = "poster_{movie_id}.{suffix}".format(movie_id=movie_id, suffix=img_suffix)
    # save an ImageField of the poster
    content = ContentFile(res.content)
    movie_obj.img.save(img_name, File(content), save=True)


def fetchPosterById(movie_id):
    """
    fetches the poster for the movie with an id of movie_id
    via the TMDB API
    """
    # check if poster exists already, if so, return 
    cur_movie = Movie.objects.get(movie_id=movie_id)
    print(cur_movie)
    if not cur_movie.img:
        config_res = get_response(CONFIG_URL)
        base_url = config_res['images']['base_url']
        poster_sizes = config_res['images']['poster_sizes']
        # select the highest resolution of posters 
        # for the current user 
        img_size = poster_sizes[-1]

        poster_url = IMAGES_BASE_URL.format(movie_id=movie_id)
        res = get_response(poster_url)['posters']
        # only take the first poster for now 
        if len(res) > 0:
            # sort posters by vote count 
            res.sort(key=operator.itemgetter('vote_count'))
            poster = res[-1]
            file_path = poster['file_path']
            # format the image url
            image_url = "{base}{size}{file}".format(base=base_url, size=img_size, file=file_path)
            save_poster(movie_id, cur_movie, image_url)
        else:
            print(res)


MAX_THREADS = 4

def fetch_images(id_arr):
    # fetch the images in threads
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(fetchPosterById, id_arr)

