"""
Bronze layer ingestion (fetch step) for TMDB movie details.

Downloads details for a targeted subset of TMDB's movie catalog
(~15-20K titles, per ADR-004), using the movie IDs already exported
in Week 3 (week3-ingestion/movie_ids.json).

This script is resumable: if it is interrupted, running it again
skips movies whose details were already saved, instead of re-fetching
everything from scratch.
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TMDB_API_TOKEN")

headers = {
    "Authorization": f"Bearer {token}",
    "accept": "application/json",
}

SAMPLE_SIZE = 20000
IDS_FILE = "week3-ingestion/movie_ids.json"
OUTPUT_PATH = "week4-bronze-layer/raw_files/tmdb_movie_details.jsonl"

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# Read the first SAMPLE_SIZE movie IDs from the full TMDB export.
movie_ids = []
with open(IDS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        movie_ids.append(record["id"])
        if len(movie_ids) >= SAMPLE_SIZE:
            break

print(f"Target sample size: {len(movie_ids)} movies")

# Find which movie IDs already have details saved, so they can be
# skipped. This makes the script safe to interrupt and re-run.
already_fetched = set()
if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                already_fetched.add(data["id"])
            except json.JSONDecodeError:
                continue

remaining_ids = [mid for mid in movie_ids if mid not in already_fetched]
print(f"Already fetched: {len(already_fetched)}")
print(f"Remaining to fetch: {len(remaining_ids)}")

session = requests.Session()
session.headers.update(headers)

with open(OUTPUT_PATH, "a", encoding="utf-8") as out_file:
    for i, movie_id in enumerate(remaining_ids, start=1):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"append_to_response": "credits,keywords"}

        try:
            response = session.get(url, params=params, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"[{i}/{len(remaining_ids)}] FAILED - id {movie_id} - network error: {e}")
            continue

        if response.status_code == 200:
            data = response.json()
            out_file.write(json.dumps(data) + "\n")
            out_file.flush()
            if i % 100 == 0:
                print(f"[{i}/{len(remaining_ids)}] OK - {data.get('title', 'unknown title')}")
        elif response.status_code == 429:
            # Rate limited: wait longer and retry this same movie once.
            print(f"[{i}/{len(remaining_ids)}] Rate limited, waiting 5s...")
            time.sleep(5)
        else:
            print(f"[{i}/{len(remaining_ids)}] FAILED - id {movie_id} - status {response.status_code}")

        time.sleep(0.05)

print("Done fetching TMDB movie details.")