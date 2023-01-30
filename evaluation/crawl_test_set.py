import asyncio
import aiohttp
import csv
import pandas as pd
import time
from math import ceil

async_batch_size = 400

# themoviedb.org api for get recommendations movie
api_key = '54bf273b2dbb4ce947cf8a27260e62b2'
endpoint = 'https://api.themoviedb.org/3/movie/{movie_id}/recommendations'

# Choosing movies for test set
df = pd.read_csv("data/movies_clean.csv")
df_filtered = df[(df["vote_average"] >= 6) & (df["vote_count"] >= 1000)]

test_id_list = list(df_filtered['id'])
print('Number of test id: ', len(test_id_list))
recommendation_list = []

# Asynchronous API call
async def fetch_recommendations(movie_id, session):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}/recommendations'
    async with session.get(url, params={'api_key': api_key}) as rsp:
        if rsp.status == 200:
            data = await rsp.json()
            recommended_id_list = [m['id'] for m in data['results']]
            return [movie_id, recommended_id_list]

async def async_recommendations_batch(movie_id_list):
    global recommendation_list
    tasks = []
    async with aiohttp.ClientSession() as session:
        for movie_id in movie_id_list:
            task = asyncio.create_task(fetch_recommendations(movie_id, session))
            tasks.append(task)

        recommendations_batch = await asyncio.gather(*tasks)
        recommendation_list += recommendations_batch
        
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

print('Crawling from themoviedb...')
start_time = time.time()

for batch in range(0, len(test_id_list), async_batch_size):
    print(f'{batch // async_batch_size + 1} / {ceil(len(test_id_list) / async_batch_size)}')
    movie_id_list = test_id_list[batch:(batch+async_batch_size)]
    asyncio.run(async_recommendations_batch(movie_id_list))

print('running time:', time.time() - start_time)

# Save results (recommendation_list) to csv
with open('data/test_set.csv', 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['id', 'recommendations'])
    writer.writerows(recommendation_list)
