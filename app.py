from flask import Flask, make_response, request
import os
import requests
import json

app = Flask(__name__)

MOVIE_DB_URL = 'https://api.themoviedb.org/3/'

API_KEY = os.environ['MOVIE_DB_API_KEY']

@app.route('/webhook', methods=['POST'])
def webhook():
  req = request.get_json(silent=True, force=True)
  res = processRequest(req)
  res = json.dumps(res, indent=4)
  print(res)
  r = make_response(res)
  r.headers['Content-Type'] = 'application/json'
  return r

def processRequest(req):
  moviesURL = MOVIE_DB_URL + 'movie/now_playing?api_key={}&language=en-US'
  genresURL = MOVIE_DB_URL + 'genre/movie/list?api_key={}&language=en-US'
  moviesURL = moviesURL.format(API_KEY)
  genresURL = genresURL.format(API_KEY)
  moviesRes = requests.post(moviesURL)
  genresRes = requests.post(genresURL)
  # TODO: Response code check
  movies = json.loads(moviesRes.text)
  genres = json.loads(genresRes.text)
  # Filter based on requested genre(s)
  params = req.get('parameters')
  specifiedGenres = params.get('movie-genre')
  selectedMovies = []
  for movieData in movies['results']:
      g = movieData['genre_ids']
  speech = "I recommend the following movies: The fugitive and air force one"
  return {
    "speech": speech,
    "displayText": speech,
    "source": 'movie-recommendations-service'
  }

if __name__ == '__main__':
    app.run(debug=False, port='8888', host='0.0.0.0')
