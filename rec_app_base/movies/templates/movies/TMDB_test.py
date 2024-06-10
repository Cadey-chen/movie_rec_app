import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

url = "https://api.themoviedb.org/3/movie/15804"

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0OWNhMTkwMGRiYmYzNmU4OTk1Y2FkOWYwMzEzNjJjNSIsInN1YiI6IjY2NTM3YWY0NTU5OTJmMmVkMDgzMWU2MSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.WyHQlqmzPahYZJQs5C-bE9JSA7ZZMa4FSStGtauFSp8"
}

response = requests.get(url, headers=headers)

formatted_res = json.dumps(json.loads(response.text), indent=2)

print(formatted_res)

# try to fetch 10 movies 
urls = [
    "https://api.themoviedb.org/3/movie/19404",
    "https://api.themoviedb.org/3/movie/372058",
    "https://api.themoviedb.org/3/movie/15804",
    "https://api.themoviedb.org/3/movie/41391",
    "https://api.themoviedb.org/3/movie/133919",
    "https://api.themoviedb.org/3/movie/455661",
    "https://api.themoviedb.org/3/movie/13",
    "https://api.themoviedb.org/3/movie/11216",
    "https://api.themoviedb.org/3/movie/19542",
    "https://api.themoviedb.org/3/movie/901",
]

def fetchMovieById(url):
    res = requests.get(url, headers=headers)
    formatted_res = json.dumps(json.loads(res.text), indent=2)
    print(formatted_res)

MAX_THREADS = 4

def main():
    # fetch the urls 
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(fetchMovieById, urls)

if __name__ == "__main__":
    main()