import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ast import literal_eval
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer 
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from fuzzywuzzy import process, fuzz

import warnings;
warnings.simplefilter('ignore')

# preprocess the the movies dataset metadata 
d_frame = pd.read_csv('./data/movies_metadata.csv')
keywords = pd.read_csv('./data/keywords.csv')
production = pd.read_csv('./data/credits.csv')
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

d_frame_byratings = d_frame[d_frame['vote_count'] > 100].sort_values('vote_average', ascending=[False])
print("Top 10 of movies with more than 100 votes ranked by average user rating")
d_frame_byratings.head(10)

# for our base movies dataframe, we filter for movies with an average rating of 7.0 or higher and 
# with the number of votes higher than the 70th percentile of all vote_count, OR popular movies
# with more than 90th percentile of vote_count and an average rating of 6.0 or higher 

v_counts = d_frame[d_frame['vote_count'].notnull()]['vote_count'].astype('int')
v_averages = d_frame[d_frame['vote_average'].notnull()]['vote_average'].astype('int')

v_70q = v_counts.quantile(0.70)
count_threshold = v_counts.quantile(0.90)
print(v_70q)
print(count_threshold)

pop_rating_thres = 6.0
qua_rating_thres = 7.0 

# next we filter the movies based on our criteria 
filtered_movies = d_frame[(d_frame['vote_count'].notnull()) & (((d_frame['vote_count'] >= count_threshold) & (d_frame['vote_average'] >= pop_rating_thres)) | ((d_frame['vote_count'] >= v_70q) & (d_frame['vote_average'] >= qua_rating_thres)))]

# create base data frame based on selecting specific fields from filtered_movies 
base_df = filtered_movies[['id','title', 'genres', 'overview', 'tagline', 'vote_count', 'vote_average', 'keywords', 'production_countries', 'production_companies', 'release_date']]

# We process the genres, keywords, crew, production_countries, production_companies 
# columns to make the data format easier to parse and analyze 

# process genres column to make only names appear 
base_df['genres'] = base_df['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

# process keywords column to make it only the tags
w_snow = SnowballStemmer('english')
base_df['keywords'] = base_df['keywords'].fillna('[]').apply(literal_eval).apply(lambda x: [j['name'] for j in x] if isinstance(x, list) else [])
base_df['kw_str'] = base_df['keywords'].apply(lambda x: ', '.join(x))
base_df['keywords'] = base_df['keywords'].apply(lambda x: [w_snow.stem(w) for w in x])

# process production_countries to make it only the country names
base_df['production_countries'] = base_df['production_countries'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'].lower().replace(" ", "") for i in x] if isinstance(x, list) else [])

# process production_companies to make it only the company and studio names
base_df['production_companies'] = base_df['production_companies'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'].lower().replace(" ", "") for i in x] if isinstance(x, list) else [])

# remove any duplicate movies
base_df = base_df.drop_duplicates(subset=['id'], keep='first')

# find the latest release_date for the movies in the dataset
release_dates = pd.to_datetime(base_df['release_date']).to_list()
max_rdate = max(release_dates)
print(max_rdate)

base_df.head(10)

# make the keywords array into a string for export into csv
base_df['keywords'] = [', '.join(map(str, i)) for i in base_df['keywords']]

# export to csv
base_df.to_csv('./data/the_movies_dataset_preprocessed.csv', index=False)
