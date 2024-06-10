import numpy as np
import pandas as pd
import os 
import matplotlib.pyplot as plt
from ast import literal_eval
from .models import Movie

import warnings;
warnings.simplefilter('ignore')

# basic recommender: we first try to recommend the top 10 movies based on ratings
# filter for vote number greater than 100
data_path = os.path.join(os.path.dirname(__file__), 'data')
d_frame_path = os.path.join(data_path, "movies_metadata.csv")
keywords_path = os.path.join(data_path, "keywords.csv")
d_frame = pd.read_csv(d_frame_path)
keywords = pd.read_csv(keywords_path)
d_frame['id'] = pd.to_numeric(d_frame['id'], errors="coerce")
keywords['id'] = pd.to_numeric(keywords['id'], errors="coerce")

d_frame = d_frame.dropna(subset=['id'])
keywords = keywords.dropna(subset=['id'])

d_frame['id'] = d_frame['id'].astype('int')
keywords['id'] = keywords['id'].astype('int')

d_frame = pd.merge(d_frame, keywords, on='id')
d_frame_byratings = d_frame[d_frame['vote_count'] > 100].sort_values('vote_average', ascending=[False])
print("Top 10 of movies with more than 100 votes ranked by average user rating")
d_frame_byratings.head(10)

# we only consider movies with more than 75% quantile of the votes  
v_counts = d_frame[d_frame['vote_count'].notnull()]['vote_count'].astype('int')
v_averages = d_frame[d_frame['vote_average'].notnull()]['vote_average'].astype('int')
v_75q = v_counts.quantile(0.75)

# next we filter the movies by count of votes 
movies_v75q = d_frame[(d_frame['vote_count'].notnull()) & (d_frame['vote_count'] >= v_75q)]

# create base data frame based on movies_v75q
base_df = movies_v75q[['id','title', 'original_title', 'genres', 'release_date', 'vote_average', 'vote_count', 'tagline', 'runtime', 'keywords', 'overview']]

# process genres column to make only names appear 
base_df['genres'] = base_df['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

# process keywords column to make it only the tags
base_df['keywords'] = base_df['keywords'].fillna('[]').apply(literal_eval).apply(lambda x: [j['name'] for j in x] if isinstance(x, list) else [])

# find the top movies by vote_average
df_by_va = base_df.sort_values('vote_average', ascending=[False])

# find the top movies by number of votes 
df_by_nv = base_df.sort_values('vote_count', ascending=[False])

# compute the median score of movies_v75q
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

# top 10 movies by average ratings 
print("Top 10 movies from all genres by average ratings:")
df_by_va.head(10)

# top 10 movies by number of ratings 
print("Top 10 movies from all genres by number of ratings (popularity)")
df_by_nv.head(10)

# top 10 movies by Bayesian average of popularity and ratings 
print("Top 10 movies from all genres by the Bayesian average of popularity and ratings ")
df_by_bavg.head(10)

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
    result_ids = []
    for index, row in result.iterrows():
        movie_id, title, desc, cur_genre, release_date, vote_count, rating = row['id'], row['title'], row['overview'], ', '.join(row['genres']), row['release_date'], row['vote_count'], row['vote_average']
        result_ids.append(movie_id)
        cur_movie = Movie(movie_id=movie_id, title=title, desc=desc, genre=cur_genre, release_date=release_date, vote_count=vote_count, rating=rating)
        cur_movie.save()
    return result_ids