import requests
import json, operator
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# fetch a movie poster image from TMDB and save the image
# to the local database

CONFIG_URL = "https://api.themoviedb.org/3/configuration"
IMAGES_BASE_URL = "https://api.themoviedb.org/3/movie/{movie_id}/images"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0OWNhMTkwMGRiYmYzNmU4OTk1Y2FkOWYwMzEzNjJjNSIsInN1YiI6IjY2NTM3YWY0NTU5OTJmMmVkMDgzMWU2MSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.WyHQlqmzPahYZJQs5C-bE9JSA7ZZMa4FSStGtauFSp8"
}

def get_response(url):
    """
    Sends a request to the API and format the response in json format
    """
    response = requests.get(url, headers=headers)
    res_json = response.json()
    formatted_res = json.dumps(json.loads(response.text), indent=2)
    # print(formatted_res)
    return res_json


def save_poster(movie_id, img_url):
    """
    save the movie poster file to the local file system 
    """
    res = requests.get(img_url)
    img_suffix = res.headers['content-type'].split('/')[-1]
    img_name = "poster_{movie_id}.{suffix}".format(movie_id=movie_id, suffix=img_suffix)
    img_path = os.path.join(".", "posters", img_name)
    # write the file into folder 
    with open(img_path, "wb") as handler:
        handler.write(res.content)


def fetchPosterById(movie_id):
    """
    fetches the poster for the movie with an id of movie_id
    via the TMDB API
    """
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
        save_poster(movie_id, image_url)
    else:
        print(res)


MAX_THREADS = 4

def main():
    # fetch the image
    fetchPosterById(68718)

if __name__ == "__main__":
    main()
