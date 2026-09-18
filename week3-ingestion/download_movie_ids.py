import gzip
import shutil
from datetime import date, timedelta
import requests

# TMDB publishes a new export daily; yesterday's file is guaranteed to exist
yesterday = date.today() - timedelta(days=1)
date_str = yesterday.strftime("%m_%d_%Y")

url = f"http://files.tmdb.org/p/exports/movie_ids_{date_str}.json.gz"
print(f"Downloading from: {url}")

response = requests.get(url, stream=True)
print(f"Status code: {response.status_code}")

if response.status_code == 200:
    gz_path = "week3-ingestion/movie_ids.json.gz"
    with open(gz_path, "wb") as f:
        f.write(response.content)

    # Decompress so we can inspect and count it easily
    json_path = "week3-ingestion/movie_ids.json"
    with gzip.open(gz_path, "rb") as f_in, open(json_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    # Each line in the file is a separate JSON object (id, original_title, etc.)
    with open(json_path, "r", encoding="utf-8") as f:
        line_count = sum(1 for _ in f)

    print(f"Total movie IDs found: {line_count}")
else:
    print("Could not download the export file. Check the date or try again later.")