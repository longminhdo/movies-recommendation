import json
import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

df = pd.read_csv('data/movies.csv')

print('Data Cleaning...', end='\t')
# Remove irrelevant / redundant fields
fields = ['adult', 'belongs_to_collection', 'budget', 'genres', 'id', 'original_language', 'overview', 'popularity', 
          'production_companies', 'release_date', 'revenue', 'runtime', 'status', 'title', 'vote_average', 'vote_count']
df = df[fields]

# Keep only the name of `genres`
df['genres'] = df['genres'].apply(json.loads)
df['genres'] = df['genres'].apply(lambda x: [i['name'] for i in x])

# Keep only the name of `production_companies`
df['production_companies'] = df['production_companies'].apply(json.loads)
df['production_companies'] = df['production_companies'].apply(lambda x: [i['name'] for i in x])

# Remove missing value of `genres` & `overview`
df['genres'].replace('[]', np.nan, inplace=True)
df['overview'].replace('^\s*$', np.nan, regex=True, inplace=True)
df['overview'].replace('No overview found.', np.nan, inplace=True)
df.dropna(subset=['genres', 'overview'], inplace=True)

# Handle missing value of `budget` & `revenue`- replace with average of median values group by genres
def fill_missing_budget_revenue(df):
    df2 = df.query('budget != 0')
    df3 = df.query('revenue != 0')

    genre_list = df['genres'].explode().unique()
    budget_dict = {}
    revenue_dict = {}

    for genre in genre_list:
        budget_dict[genre] = df2[df2['genres'].apply(lambda x: genre in x)]['budget'].median()
        revenue_dict[genre] = df3[df3['genres'].apply(lambda x: genre in x)]['revenue'].median()
        
    def avg_median(row, median_dict):
        genre_medians = [median_dict[g] for g in row['genres']]
        return sum(genre_medians) / len(genre_medians)
    
    df['budget'] = df.apply(lambda row: avg_median(row, budget_dict) if row['budget'] == 0 else row['budget'], axis=1)
    df['revenue'] = df.apply(lambda row: avg_median(row, revenue_dict) if row['revenue'] == 0 else row['revenue'], axis=1)

fill_missing_budget_revenue(df)
print('Done')

print('Feature Engineering...', end='\t')
# Create `keywords` field
stop_words = set(stopwords.words('english'))
stemmer = SnowballStemmer("english")

def get_keywords_string(overview):
    # Remove punctuation
    overview = re.sub(r'[^\w\s]','',overview)
    # Tokenize the text
    overview = overview.split()
    # Remove stopwords
    overview = [word for word in overview if word.lower() not in stop_words]
    # Stemming
    words = [stemmer.stem(word) for word in overview]
    return ' '.join(words)

df['keywords'] = df['overview'].apply(get_keywords_string)

# Combine element of list into a single string (element is removed space and to lowercase)
def combine_features_to_string(item_list):
    return ' '.join([str.lower(i.replace(" ", "")) for i in item_list])

# Create `metadata` field
df['metadata'] = df['genres'].apply(combine_features_to_string) + ' ' + \
                 df['production_companies'].apply(combine_features_to_string) + ' ' + \
                 df['original_language']
print('Done')

df.to_csv('data/movies_clean.csv', index=False)
