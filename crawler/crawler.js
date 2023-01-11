import * as dotenv from 'dotenv';
import fetch from 'node-fetch';
import * as fsLibrary from 'fs';

globalThis.fetch = fetch;
dotenv.config();

const apiKey = process.env.API_KEY;

const writeFile = async (fileName, data) => {
  await fsLibrary.writeFile(fileName, data, (error) => {
    if (error) throw err;
  });
};

const execution = async () => {
  for (let chunk = 0; chunk < 200; chunk++) {
    const result = [];
    for (let i = chunk * 5000; i < (chunk + 1) * 5000; i += 250) {
      const promises = [];
      for (let movieId = i; movieId <= i + 250; movieId++) {
        promises.push(
          fetch(
            `https://api.themoviedb.org/3/movie/${movieId}?api_key=${apiKey}`,
          ),
        );
      }
      try {
        const res = await Promise.all(promises);
        for (let j = 0; j < res?.length; j++) {
          if (res[j]?.status === 200) {
            const data = await res[j].json();
            result.push(data);
          }
        }
      } catch (error) {
        console.log(error);
      }
      console.log(`${i + 250}/1000000`);
    }

    writeFile(`movies_${chunk}.json`, JSON.stringify(result));
  }
};

execution();
