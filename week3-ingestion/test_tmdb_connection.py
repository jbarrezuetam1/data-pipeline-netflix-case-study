import os
import requests
from dotenv import load_dotenv

#Load variables from the .env file into this run's environment
load_dotenv()

token = os.getenv("TMDB_API_TOKEN")

if not token:
	print("ERROR: TMDB_API_TOKEN not found. Check that the .env file exists and the variable is spelled correctly.")
	exit()

print(f"Token loaded successfully (ends with: ...{token[-6:]})")

#Test call: fetch details for a well-known movie (Fight Club, id 550)
url = "https://api.themoviedb.org/3/movie/550"
headers = {
	"Authorization": f"Bearer {token}",
	"accept": "application/json"
}

response = requests.get(url, headers=headers)

print(f"Status code: {response.status_code}")

if response.status_code == 200:
	data = response.json()
	print(f"Title: {data['title']}")
	print(f"Release date: {data['release_date']}")
	print(f"Average rating: {data['vote_average']}")
else:
	print(f"Error in response: {response.text}")