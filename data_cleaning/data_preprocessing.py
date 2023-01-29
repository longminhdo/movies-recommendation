import pandas as pd
import re
from ast import literal_eval
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

df = pd.read_csv('../data/movies.csv')

# Keep only the name of `genres`
df['genres'] = df['genres'].apply(literal_eval)
df['genres'] = df['genres'].apply(lambda x: [i['name'] for i in x])

# Keep only the name of `production_companies`
df['production_companies'] = df['production_companies'].apply(literal_eval)
df['production_companies'] = df['production_companies'].apply(lambda x: [i['name'] for i in x])

# # Handle missing value of `budget` - replace with median value
# median_budget = df[df['budget'] != 0]['budget'].median()
# df.loc[df['budget'] == 0, 'budget'] = median_budget

# # Handle missing value of `revenue` - replace with median value
# median_revenue = df[df['revenue'] != 0]['revenue'].median()
# df.loc[df['revenue'] == 0, 'revenue'] = median_revenue

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

df.to_csv('data/movies_clean.csv', index=False)
