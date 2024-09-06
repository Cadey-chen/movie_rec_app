import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv

import warnings;
warnings.simplefilter('ignore')

# load TMDB movies dataset 
tmdb_dframe = pd.read_csv('./data/TMDB_movie_dataset.csv')
tmdb_dframe['date_formal'] = pd.to_datetime(tmdb_dframe['release_date'])

tmdb_dframe[tmdb_dframe['title'] == 'Inception']

# for our base movies dataframe, we filter for movies with an average rating of 7.5 or higher and 
# with the number of votes higher than the 97.5 percentile of all vote_count, OR popular movies
# with more than 99 percentile of vote_count and an average rating of 6.8 or higher 

v_counts = tmdb_dframe[tmdb_dframe['vote_count'].notnull()]['vote_count'].astype('int')
v_averages = tmdb_dframe[tmdb_dframe['vote_average'].notnull()]['vote_average'].astype('int')

v_97q = v_counts.quantile(0.975)
count_threshold = v_counts.quantile(0.99)
print(v_97q)
print(count_threshold)

pop_rating_thres = 6.8
qua_rating_thres = 7.2

# next we filter the movies based on our criteria 
filtered_movies = tmdb_dframe[(tmdb_dframe['vote_count'].notnull()) & (((tmdb_dframe['vote_count'] >= count_threshold) & (tmdb_dframe['vote_average'] >= pop_rating_thres)) | ((tmdb_dframe['vote_count'] >= v_97q) & (tmdb_dframe['vote_average'] >= qua_rating_thres)))]

# create base data frame based on selecting specific fields from filtered_movies 
tmdb_dframe = filtered_movies[['id','title', 'genres', 'overview', 'tagline', 'vote_count', 'vote_average', 'keywords', 'production_countries', 'production_companies', 'release_date']]
tmdb_dframe.shape

tmdb_dframe.dtypes

tmdb_dframe.head(10)

# read in the preprocessed the movies dataset
themovies_dframe = pd.read_csv('./data/the_movies_dataset_preprocessed.csv')
themovies_dframe.head(10)

# create a new genres_list column 
tmdb_dframe['genres'] = tmdb_dframe['genres'].fillna('')
tmdb_dframe['genres_list'] = tmdb_dframe['genres'].apply(lambda x: [item.strip() for item in x.split(',')])

# merge with the movies dataset for movies released on or before 2017-08-18
themovies_dframe.set_index('id', inplace=True)
tmdb_dframe.set_index('id', inplace=True)
tmdb_dframe.loc[(tmdb_dframe['release_date'] <= '2017-08-18'), 'genres'] = tmdb_dframe.loc[(tmdb_dframe['release_date'] <= '2017-08-18')].index.map(
    lambda i: themovies_dframe.at[i, 'gr_str'] if i in themovies_dframe.index else tmdb_dframe.at[i, 'genres']
)
tmdb_dframe.loc[(tmdb_dframe['release_date'] <= '2017-08-18'), 'keywords'] = tmdb_dframe.loc[(tmdb_dframe['release_date'] <= '2017-08-18')].index.map(
    lambda i: themovies_dframe.at[i, 'kw_str'] if i in themovies_dframe.index else tmdb_dframe.at[i, 'keywords']
)
tmdb_dframe.loc[(tmdb_dframe['release_date'] <= '2017-08-18'), 'overview'] = tmdb_dframe.loc[(tmdb_dframe['release_date'] <= '2017-08-18')].index.map(
    lambda i: themovies_dframe.at[i, 'overview'] if i in themovies_dframe.index else tmdb_dframe.at[i, 'overview']
)

# create base data frame based on selecting specific fields from tmdb_dframe
base_df = tmdb_dframe[['title', 'genres', 'overview', 'tagline', 'vote_count', 'vote_average', 'keywords', 'production_countries', 'production_companies', 'release_date']]

base_df.head(10)

# export the processed dataframe, base_df to a csv file 
base_df.to_csv('./data/base_data.csv')

# read base_data.csv
saved_base_df = pd.read_csv('./data/base_data.csv')
saved_base_df.head(10)