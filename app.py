from flask import Flask, make_response, request
import os
import requests
import json

app = Flask(__name__)

# Database that provides simple genre filtering.
MOVIE_DB_URL = 'https://api.themoviedb.org/3/'
API_KEY = os.environ['MOVIE_DB_API_KEY']

# Maximum number of movies that are returned after all filtering.
MAX_RECS = 5

@app.route('/', methods=['GET'])
def index():
    return "Hello, World!"

@app.route('/webhook', methods=['POST'])
def webhook():
  req = request.get_json(force=True)
  res = processRequest(req)
  r = make_response(json.dumps(res))
  r.headers['Content-Type'] = 'application/json'
  return r

def processRequest(req):
  genresURL = (MOVIE_DB_URL + 'genre/movie/list?api_key={}&language=en-US').format(API_KEY)
  moviesURL = (MOVIE_DB_URL + 'movie/now_playing?api_key={}&language=en-US').format(API_KEY)
  moviesRes = requests.get(moviesURL)
  genresRes = requests.get(genresURL)
  #TODO: Response code check
  allMovies = json.loads(moviesRes.text)
  allGenres = json.loads(genresRes.text)
  # Map a genre to a genre id given the response from the movie database.
  genreMap = {}
  for genre in allGenres['genres']:
      genreMap[genre['name']] = genre['id']
  # Filter movies based on requested genre(s).
  specifiedGenresEnglish = req.get('result').get('parameters').get('movie-genre')
  # The genres provided by api.ai are english words so we need to convert them to numbers.
  specifiedGenresID = []
  for genre in specifiedGenresEnglish:
      specifiedGenresID.append(genreMap[genre])
  selectedMovies = []
  maxRecs = MAX_RECS
  for movieData in allMovies['results']:
      # All the listed genres for this movie.
      genres = movieData['genre_ids']
      # All of the specified genres must be present in the genre list for the current movie we are looking at.
      if all(x in genres for x in specifiedGenresID) and maxRecs > 0:
        selectedMovies.append(movieData['title'])
        maxRecs -= 1
  if len(selectedMovies) == 0:
      speech = "Sorry, there are no movies currently playing that match your request."
  else:
      speech= "I recommend the following movies: " + ', '.join(selectedMovies)
  # The outbound context are the movies that are recommended
  return {
    "speech": speech,
    "displayText": speech,
    "contextOut": [{"name":"recommendations", "lifespan":2, "parameters":{"recommendations":selectedMovies}}],
    "source": 'movie-recommendations-service'
  }

if __name__ == '__main__':
    app.run(debug=False, port='8888', host='0.0.0.0')
