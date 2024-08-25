import numpy as np
import pandas as pd
import os 
import matplotlib.pyplot as plt
from ast import literal_eval
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer 
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from fuzzywuzzy import process, fuzz
from .models import Movie
from concurrent.futures import ThreadPoolExecutor, wait
from .process_images import fetchPosterById

import warnings;
warnings.simplefilter('ignore')

# basic recommender: we first try to recommend the top movies based on ratings
# or popularity or the Bayesian average of ratings and popularity 

# preprocess the movies metadata 
data_path = os.path.join(os.path.dirname(__file__), 'data')
d_frame_path = os.path.join(data_path, "movies_metadata.csv")
keywords_path = os.path.join(data_path, "keywords.csv")
production_path = os.path.join(data_path, "credits.csv")

d_frame = pd.read_csv(d_frame_path)
keywords = pd.read_csv(keywords_path)
production = pd.read_csv(production_path)

d_frame['id'] = pd.to_numeric(d_frame['id'], errors="coerce")
keywords['id'] = pd.to_numeric(keywords['id'], errors="coerce")
production['id'] = pd.to_numeric(production['id'], errors="coerce")

d_frame = d_frame.dropna(subset=['id'])
keywords = keywords.dropna(subset=['id'])
production = production.dropna(subset=['id'])

d_frame['id'] = d_frame['id'].astype('int')
keywords['id'] = keywords['id'].astype('int')
production['id'] = production['id'].astype('int')

d_frame = pd.merge(d_frame, keywords, on='id')
d_frame = pd.merge(d_frame, production, on='id')

# for our base movies dataframe, we filter for movies with an average rating of 7.0 or higher and 
# with the number of votes higher than the 70th percentile of all vote_count, OR popular movies
# with more than 90th percentile of vote_count and an average rating of 6.0 or higher 

v_counts = d_frame[d_frame['vote_count'].notnull()]['vote_count'].astype('int')
v_averages = d_frame[d_frame['vote_average'].notnull()]['vote_average'].astype('int')

v_70q = v_counts.quantile(0.70)
count_threshold = v_counts.quantile(0.90)

pop_rating_thres = 6.0
qua_rating_thres = 7.0 

# next we filter the movies based on our criteria 
filtered_movies = d_frame[(d_frame['vote_count'].notnull()) & (((d_frame['vote_count'] >= count_threshold) & (d_frame['vote_average'] >= pop_rating_thres)) | ((d_frame['vote_count'] >= v_70q) & (d_frame['vote_average'] >= qua_rating_thres)))]

# create base data frame based on selecting specific fields from filtered_movies 
base_df = filtered_movies[['id','title', 'genres', 'overview', 'tagline', 'vote_count', 'vote_average', 'keywords', 'crew', 'production_countries', 'production_companies', 'release_date']]

# helper function to help us extract the director and writers 
# from the crew column
def director_and_writer(crew):
    crew_arr = []
    for rec in crew:
        if rec['job'] == 'Director' or rec['job'] == 'Screenplay':
            crew_arr.append(rec['name'].lower().replace(" ", ""))
    return crew_arr

# We process the genres, keywords, crew, production_countries, production_companies 
# columns to make the data format easier to parse and analyze 

# process genres column to make only names appear 
base_df['genres'] = base_df['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

# process keywords column to make it only the tags
w_snow = SnowballStemmer('english')
base_df['keywords'] = base_df['keywords'].fillna('[]').apply(literal_eval).apply(lambda x: [j['name'] for j in x] if isinstance(x, list) else [])
base_df['keywords'] = base_df['keywords'].apply(lambda x: [w_snow.stem(w) for w in x])

# process crew to make it only director and writer 
base_df['crew'] = base_df['crew'].fillna('[]').apply(literal_eval).apply(director_and_writer)

# process production_countries to make it only the country names
base_df['production_countries'] = base_df['production_countries'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'].lower().replace(" ", "") for i in x] if isinstance(x, list) else [])

# process production_companies to make it only the company and studio names
base_df['production_companies'] = base_df['production_companies'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'].lower().replace(" ", "") for i in x] if isinstance(x, list) else [])

# only keep unique ids in base_df
base_df = base_df.drop_duplicates(subset=['id'], keep='first')

# find the top movies by vote_average
df_by_va = base_df.sort_values('vote_average', ascending=[False])

# find the top movies by number of votes 
df_by_nv = base_df.sort_values('vote_count', ascending=[False])

# prepare coefficients for Bayesian average of ratings 
# and popularity calculation 

# compute the median score of base_df
median_rating = base_df['vote_average'].median()

# Use Bayesian average to compute a combined measure for average user rating + popularity 
overall_average_rating = base_df['vote_average'].mean()

average_counts = base_df['vote_count'].mean()

global_c = average_counts * overall_average_rating

def bayesian_average(mrow):
    cur_movie_rating = mrow['vote_average']
    total_votes = mrow['vote_count']
    b_avg = ((cur_movie_rating * total_votes) + global_c) / (average_counts + total_votes)
    return b_avg

base_df['bavg_rating'] = base_df.apply(bayesian_average, axis=1)

df_by_bavg = base_df.sort_values('bavg_rating', ascending=[False])

# save_movie takes in a pandas dataframe of movie metadata 
# saves these movies into the database if not already saved,
# and appends the ids in order 
def save_movie(movie):
    if Movie.objects.filter(movie_id=movie['id']).exists():
            return
    movie_id, title, desc, cur_genre, release_date, vote_count, rating = movie['id'], movie['title'], movie['overview'], ', '.join(movie['genres']), movie['release_date'], movie['vote_count'], movie['vote_average']
    cur_movie = Movie(movie_id=movie_id, title=title, desc=desc, genre=cur_genre, release_date=release_date, vote_count=vote_count, rating=rating)
    cur_movie.save()
    fetchPosterById(movie_id)
    movie_obj = Movie.objects.get(movie_id=movie_id)
    print(movie_obj)

# write_movies writes movies in movies_list as data objects into the database 
def write_movies(movies_list):
    # save result to db
    MAX_THREADS = 5
    # write movie objects in threads 
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(save_movie, row) for idx, row in movies_list.iterrows()]
        wait(futures)

# a method to recommend the top movies from each genre 
def movies_by_genre(genre, query_type, selection):
    result = pd.DataFrame()
    match query_type:
        case "popularity":
            result = df_by_nv[(df_by_nv["genres"].notnull()) & (df_by_nv["genres"].apply(lambda x: genre in x))]
        case "ratings":
            result = df_by_va[(df_by_nv["genres"].notnull()) & (df_by_va["genres"].apply(lambda x: genre in x))]
        case "bayesian":
            result = df_by_bavg[(df_by_nv["genres"].notnull()) & (df_by_bavg["genres"].apply(lambda x: genre in x))]
    result = result.head(selection)
    # save result to db
    result_ids = result['id'].values
    write_movies(result)
    return result_ids

# Use TF-IDF Vectorizer to help us find similarities between movie descriptions 
def find_cosine_sim(df1, df1_column, df2, df2_column):
    # Use TF-IDF Vectorizer to find similarity scores between movie descriptions
    tfid_vec = TfidfVectorizer(analyzer='word', ngram_range=(1,3), stop_words='english')
    tfid_vec.fit(df1[df1_column])
    df_matrix = tfid_vec.transform(df1[df1_column])

    tfid_vec_2 = TfidfVectorizer(analyzer='word', ngram_range=(1,3), stop_words='english')
    tfid_vec_2.fit(df2[df2_column])
    df_matrix_2 = tfid_vec.transform(df2[df2_column])
    
    # calculate the cosine similarity score between the user defined movie and the movies in the db
    cos_score = linear_kernel(df_matrix, df_matrix_2)
    
    return cos_score

# next, we build a content-based recommender on the base movies 
# we use overview + keywords + tagline for the basis of our comparison 
base_df['overview'] = base_df['overview'].fillna('')
base_df['tagline'] = base_df['tagline'].fillna('')
base_df['kw_str'] = base_df['keywords'].apply(lambda x: ' '.join(x))
base_df['genres_str'] = base_df['genres'].apply(lambda x: ' '.join(x))
base_df['crew_str'] = base_df['crew'].apply(lambda x: ' '.join(x))
base_df['countries_str'] = base_df['production_countries'].apply(lambda x: ' '.join(x))
base_df['studios_str'] = base_df['production_companies'].apply(lambda x: ' '.join(x))
base_df['desc'] = base_df['overview'] + ' ' + base_df['tagline'] + ' ' + base_df['kw_str'] + ' ' + base_df['genres_str'] + ' ' + base_df['crew_str'] + ' ' + base_df['countries_str']
base_df['short_desc'] = base_df['overview'] + ' ' + base_df['tagline'] + ' ' + base_df['kw_str'] + ' ' + base_df['genres_str']
tfid_vec = TfidfVectorizer(analyzer='word', ngram_range=(1,3), stop_words='english')
tfid_vec.fit(base_df['desc'])
df_matrix = tfid_vec.transform(base_df['desc'])

# calculate the cosine similarity score between each movie 
cos_sim_score = linear_kernel(df_matrix, df_matrix)

base_df[base_df['title'] == 'La La Land']

base_df = base_df.reset_index()
title_indices = pd.Series(base_df.index, index=base_df['title'])
id_indices = pd.Series(base_df.index, index=base_df['id'])

# find similar movies by description
# find similar movies by description
def sim_movies_by_desc(movie_id=None, movie_title=None):
    idx = 0
    if movie_id:
        idx = id_indices[movie_id]
    if movie_title:
        idx = title_indices[movie_title]
    cos_arr = cos_sim_score[idx]
    scores = sorted(list(enumerate(cos_arr)), key=lambda x: x[1], reverse=True)
    top_match = [(x[0], x[1]*100) for x in scores[1:26]]
    movie_indices = [m[0] for m in top_match]
    match_dict = dict(top_match)
    matched_movies = base_df.iloc[movie_indices]
    matched_movies['desc_sim'] = matched_movies.index.map(match_dict) 
    return matched_movies

# overall_sim is the average of desc_sim and tags_sim, when 
# one of the similarity is lower than 25 percentile, this means 
# either the description or the tags is very different from the 
# source movie, then we make the overall similarity to be zero
def find_overall_sim(target_movie, desc_limit, tags_limit, desc_prop, tags_prop):
    if target_movie['desc_sim'] < desc_limit or target_movie['tags_sim'] < tags_limit:
        return 0
    else:
        return ((target_movie['desc_sim'] * desc_prop) + (target_movie['tags_sim'] * tags_prop))
    

# sort the list of movies by overall similarity scores 
def rank_movies_overall(movies_list, desc_prop, tags_prop):
    desc_25q = movies_list['desc_sim'].quantile(0.25)
    tags_25q = movies_list['tags_sim'].quantile(0.25)
    
    # overall_sim is the overall similarity of both desc_sim and tags_sim
    movies_list['overall_sim'] = movies_list.apply(find_overall_sim, axis=1, args=(desc_25q, tags_25q, desc_prop, tags_prop))
    
    # sort by overall_sim 
    sorted_movies = movies_list.sort_values(by=['overall_sim'], ascending=False)
    return sorted_movies


# come up with custom similarity scores on a scale of 1 - 10 between the source movie and target movies 
def calculate_score(target_movie, src_kw, src_gr, src_st, src_va):
    # source movie is the movie we wish to find similar movies for
    # we take the similarities in keyword (40%), genres(30%), studio (15%), and ratings (15%) into consideration
    maj_weight_factor = 4.0
    med_weight_factor = 3.0
    min_weight_factor = 1.5
    kw_sim = (len(np.intersect1d(src_kw, target_movie['keywords'])) / len(src_kw)) * maj_weight_factor
    gr_sim = (len(np.intersect1d(src_gr, target_movie['genres'])) / len(src_gr)) * med_weight_factor
    st_sim = (len(np.intersect1d(src_st, target_movie['production_companies'])) / len(src_st)) * min_weight_factor
    # formula for calculating rating similarity 1 - (abs(rating diff))/(source rating)
    va_sim = (1 - abs(src_va - target_movie['vote_average'])/src_va) * min_weight_factor
    tags_sim = gr_sim + kw_sim + st_sim + va_sim
    return tags_sim


def find_matches(movie_id=None, movie_title=None, num_movies=0):
    target_movies = None
    if movie_id:
        target_movies = sim_movies_by_desc(movie_id, None).head(25)
    if movie_title:
        target_movies = sim_movies_by_desc(None, movie_title).head(25)
        movie_id = base_df[base_df['id'] == movie_id]['id'].item()
    target_movies = sim_movies_by_desc(movie_id, movie_title).head(25)
    # find similaritie score for the movies returned 
    src = base_df[base_df['id'] == movie_id]
    
    # tags_sim is the similarity between genres, keywords, ratings, and popularity tags 
    target_movies['tags_sim'] = target_movies.apply(calculate_score, axis=1, args=(src['keywords'].to_list()[0], src['genres'].to_list()[0], src['production_companies'].to_list()[0], src['vote_average']))
    
    # sort the movies list by overall similarity score of tags and description
    sorted_movies = rank_movies_overall(target_movies, 0.20, 0.80)
    result = sorted_movies.head(num_movies)
    # save result to db
    result_ids = result['id'].values
    write_movies(result)
    return result_ids


MAX_VOTE_COUNT = base_df['vote_count'].max()

# come up with custom similarity scores on a scale of 1 - 10 between the source movie and target movies 
def find_sim_score(target_movie, src_kw, src_gr):
    # source movie is the movie we wish to find similar movies for
    # we take the similarities in keywords (40%), genres (30%), bayesian average(30%) into consideration
    # and take the average of this score with the desc_sim score 
    maj_weight_factor = 4.0
    med_weight_factor = 3.0
    min_weight_factor = 1.5
    perfect_score = 10
    kw_sim = (len(np.intersect1d(src_kw, target_movie['keywords'])) / len(src_kw)) * maj_weight_factor
    gr_sim = (len(np.intersect1d(src_gr, target_movie['genres'])) / len(src_gr)) * med_weight_factor
    # give higher ranks to movies with a higher bayesian average 
    va_sim = (target_movie['bavg_rating']/10) * med_weight_factor
    tags_sim = gr_sim + kw_sim + va_sim
    return tags_sim


# a movie recommender that recommends 10 films based on user input
def user_defined_recommender(input_genres, input_keywords, input_overview, num_movies):
    # parse and process input data
    genres = [input_genres]
    keywords = [input_keywords]
    overview = [input_overview]
    desc_obj = {'genres': genres, 'keywords': keywords, 'overview': overview}
    desc_df = pd.DataFrame(data=desc_obj)
    w_snow = SnowballStemmer('english')
    desc_df['keywords'] = desc_df['keywords'].apply(lambda x: [w_snow.stem(w) for w in x])
    desc_df['genres_str'] = desc_df['genres'].apply(lambda x: ' '.join(x))
    desc_df['keywords_str'] = desc_df['keywords'].apply(lambda x: ' '.join(x))
    desc_df['desc'] = desc_df['overview'] + ' ' + desc_df['genres_str'] + ' ' + desc_df['keywords_str']
    
    # Use TF-IDF Vectorizer to find similarity scores between movie descriptions
    cos_score = find_cosine_sim(base_df, 'short_desc', desc_df, 'desc')
    
    scores = sorted(list(enumerate(cos_score)), key=lambda x: x[1], reverse=True)
    top_match = [(x[0], (x[1][0] * 100)) for x in scores[1:26]]
    match_dict = dict(top_match)
    movie_indices = [m[0] for m in top_match]
    matched_movies = base_df.iloc[movie_indices]
    matched_movies['desc_sim'] = matched_movies.index.map(match_dict) 
    
    # tags_sim is the similarity between genres, keywords, ratings, and popularity tags 
    matched_movies['tags_sim'] = matched_movies.apply(find_sim_score, axis=1, args=(desc_df['keywords'].to_list()[0], desc_df['genres'].to_list()[0]))
    
    # sort the movies list by overall similarity score of tags and description
    sorted_movies = rank_movies_overall(matched_movies, 0.50, 0.50)
    
    result = sorted_movies.head(num_movies)
    # save result to db
    result_ids = []
    return result_ids


movie_title_list = base_df['title'].unique().tolist()

# find_sim_titles finds similar movie names in the db with the input_title supplied 
# based on string comparison 
def find_sim_titles(input_title):
    results = process.extract(input_title, movie_title_list, scorer=fuzz.token_set_ratio)
    titles = map(lambda x: x[0], results)
    return list(titles)

# find the movie in base_df based on title 
def movie_by_title(title, title_arr):
    movie = base_df[base_df['title'] == title]
    if movie.shape[0] == 1:
        title_arr.append({'title': movie['title'].item(), 'release_date': movie['release_date'].item(), 'id': movie['id'].item()})
    else:
        for idx, row in movie.iterrows():
            title_arr.append({'title': row['title'], 'release_date': row['release_date'], 'id': row['id']})

# process_sim_titles finds movie titles of a similar title 
# and generates an array of movie title and release_date in tuples 
def process_sim_titles(input_title):
    sim_titles = find_sim_titles(input_title)
    title_arr = []
    for title in sim_titles:
        movie_by_title(title, title_arr)
    return title_arr

