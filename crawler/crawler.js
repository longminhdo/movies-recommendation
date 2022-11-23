import * as dotenv from "dotenv";
dotenv.config();
import fetch from "node-fetch";
globalThis.fetch = fetch;
import * as fsLibrary from "fs";

var apiKey = process.env.API_KEY;

const writeFile = (fileName, data) => {
  fsLibrary.writeFile(fileName, data, (error) => {
    if (error) throw err;
  });
};

const execution = async () => {
  const result = [];
  for (let i = 0; i < 1000; i += 50) {
    const promises = [];
    for (let movieId = i; movieId < i + 50; movieId++) {
      promises.push(
        fetch(`https://api.themoviedb.org/3/movie/3?api_key=${apiKey}`)
      );
    }
    const res = await Promise.all(promises);
    for (let j = 0; j < res?.length; j++) {
      if (res[j]?.status === 200) {
        const data = await res[j].json();
        result.push(data);
      }
    }
  }

  writeFile("movies.json", JSON.stringify(result));
};

execution();
