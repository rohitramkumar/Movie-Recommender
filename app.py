from flask import Flask, make_response, request
import os
import requests
import json

app = Flask(__name__)

MOVIE_DB_URL = 'https://api.themoviedb.org/3/'

API_KEY = os.environ['MOVIE_DB_API_KEY']

# Maximum number of movies that are returned after initial genre filtering.
MAX_RECS = 10

@app.route('/webhook', methods=['POST'])
def webhook():
  req = request.get_json(silent=True, force=True)
  res = processRequest(req)
  r = make_response(res)
  r.headers['Content-Type'] = 'application/json'
  return r

def processRequest(req):
  genresURL = (MOVIE_DB_URL + 'genre/movie/list?api_key={}&language=en-US').format(API_KEY)
  moviesURL = (MOVIE_DB_URL + 'movie/now_playing?api_key={}&language=en-US').format(API_KEY)
  moviesRes = requests.post(moviesURL)
  genresRes = requests.post(genresURL)
  # TODO: Response code check
  allMovies = json.loads(moviesRes.text)
  allGenres = json.loads(genresRes.text)
  # Map a genre to a genre id given the response from the movie database.
  genreMap = {}
  for genre in allGenres['genres']
      genreMap[genre['name']] = genre['id']
  # Filter movies based on requested genre(s).
  specifiedGenresEnglish = req.get('result').get('parameters').get('movie-genres')
  # The genres provided by api.ai are english words so we need to convert them to numbers.
  specifiedGenresID = []
  for genre in specifiedGenresEnglish:
      specifiedGenresID.append(genreMap[genre])
  # The genres of each movie returned from movie DB are in order so we do the same for the specified genres.
  sort(specifiedGenresID)
  selectedMovies = []
  for movieData in allMovies['results']:
      # All the listed genres for this movie.
      genres = movieData['genre_ids']
      # All of the specified genres must be present in the genre list for the current movie we are looking at.
      if cmp(specifiedGenresID, genres) == 0 and MAX_RECS > 0:  
        selectedMovies.append(movieData['title'])
        MAX_RECS -= 1
  # If the user provided a rating, then filter movies further based on Rotten Tomatoes percentage.

  # Rotten tomatoes provides no API, so scraping is required.
  speech = "I recommend the following movies: " + ', '.join(selectedMovies)
  return {
    "speech": speech,
    "displayText": speech,
    "source": 'movie-recommendations-service'
  }

if __name__ == '__main__':
    app.run(debug=False, port='8888', host='0.0.0.0')
