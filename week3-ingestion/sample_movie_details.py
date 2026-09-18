import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TMDB_API_TOKEN")

headers = {
    "Authorization":f"Bearer {token}",
    "accept":"application/json"
}

# Read the movie IDs file we downloaded earlier.
# Each line is its own small JSON object, e.g. {"id": 550, "original_title": "Fight Club", ...}
sample_size = 20
movie_ids = []

with open("week3-ingestion/movie_ids.json","r", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        movie_ids.append(record["id"])
        if len(movie_ids) >= sample_size:
            break

print(f"Fetching details for {len(movie_ids)} sample movies...")

output_path = "week3-ingestion/sample_movie_details.jsonl"

with open(output_path, "w", encoding="utf-8") as out_file:
    for i, movie_id in enumerate(movie_ids, start=1):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"append_to_response" : "credits,keywords"}

        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data =response.json()
            # Write the raw response as one line of JSON (JSON Lines format)
            out_file.write(json.dumps(data) + "\n")
            print(f"[{i}/{len(movie_ids)}] OK - {data.get('title', 'unknown title')}")
        else:
            print(f"[{i}/{len(movie_ids)}] FAILED - id {movie_id} - status {response.status_code} - {response.text}")

        # Small pause to be a respectful API citien, even within the free-tier limits
        time.sleep(0.3)

print(f"Done. Raw data saved to {output_path}")