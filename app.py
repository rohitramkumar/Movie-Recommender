from flask import Flask, url_for, make_response, send_file, request, jsonify, render_template
from flask_bootstrap import Bootstrap
from utils import MovieDBApiClient, MOVIE_DISCOVERY_URL, spellCheck
import json

app = Flask(__name__)
Bootstrap(app)

@app.route("/")
def index():
  # return make_response(open('templates/index.html').read())
  return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
  """This Flask route receives all requests from API.ai and processes these
  requests according to the action specified by the user"""

  req = request.get_json(force=True)
  action = req.get('result').get('action')
  if action == "movie.filtering":
    res = processFilteringRequest(req)
  elif action == "movie.similar":
    res = processSimilarityRequest(req)
  r = make_response(json.dumps(res))
  r.headers['Content-Type'] = 'application/json'
  return r

def processFilteringRequest(req):
  """This function deals with processing the movie filters provided by a user
  and feeding these filters into api calls for a movie database. The filtered
  movies returned from these api calls are returned to the user."""

  client = MovieDBApiClient()
  finalDiscoveryURL = MOVIE_DISCOVERY_URL
  userSpecifiedData = req.get('result').get('contexts')[0]
  # Get all filters specified by user on api.ai.
  userSpecifiedGenres = userSpecifedData.get('parameters').get('genre')
  userSpecifiedCastFirstName = userSpecifedData.get('parameters').get('cast-first-name')
  userSpecifiedCastLastName = userSpecifedData.get('parameters').get('cast-last-name')
  # Chat agent only allows us to parse out first and last names seperately
  # so we need to merge these to get a list of full names.
  userSpecifiedCast = [s1 + " " + s2 for s1, s2 in zip(userSpecifiedCastFirstName, userSpecifiedCastLastName)]
  userSpecifiedCast = map(spellCheck, userSpecifiedCast)
  userSpecifiedRating = userSpecifedData.get('parameters').get('rating')
  # Get movie database information using previously instantiated API client.
  genreIds = client.getGenresIds(userSpecifiedGenres)
  castIds = client.getCastIds(userSpecifiedCast)
  # Construct movie discovery URL.
  finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('with_genres', genreIds))
  finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('with_people', castIds))
  finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('certification', userSpecifiedRating))
  movies = client.getDiscoveredMovies(finalDiscoveryURL)
  return prepareResponse(similarMovies)

def processSimilarityRequest(req):
  """The function deals with processing a single movie provided by the user and
  returning a list of movies which are similar."""
  client = MovieDBApiClient()
  benchmarkMovie = req.get('result').get('contexts')[0].get('parameters').get('benchmark')
  benchmarkMovie = spellCheck(benchmarkMovie)
  similarMovies = client.getSimilarMovies(benchmarkMovie)
  return prepareResponse(similarMovies)

def prepareResponse(movies):
  """Helper function that prepares the return object we send to the user
   given a list of movies."""
  if len(movies) > 0:
    speech = "I recommend the following movies: " + ', '.join(movies)
  else:
    speech = "Sorry there are no movies that match your request"
  return {
    "speech":speech,
    "displayText":speech,
    "source":"movie-recommendation-service"
  }

if __name__ == '__main__':
  app.run(debug=True, port='8888', host='0.0.0.0')
