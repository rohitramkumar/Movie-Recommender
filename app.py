from flask import Flask, url_for, make_response, send_file, request, jsonify, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow

from utils import APIAI_KEY, MovieDBApiClient, LearningAgentClient, MOVIE_DISCOVERY_URL, spellCheck, createUser, login
import apiai
import os
import requests
import json
import sys
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
Bootstrap(app)
db = SQLAlchemy(app)
# ma = Marshmallow(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/api/login/", methods=['POST'])
def login():
    user_detail = json.loads(request.data)
    username = user_detail.get("username")
    password = user_detail.get("password")
    return jsonify(login(username, password))

@app.route("/api/signup/", methods=['POST'])
def signup():
    new_user = json.loads(request.data)
    first_name = new_user.get("firstname")
    last_name = new_user.get("lastname")
    username = new_user.get("username")
    password = new_user.get("password")
    return createUser(username, password, first_name, last_name)

@app.route('/webhook', methods=['POST'])
def webhook():
    """This Flask route receives all requests from API.ai and processes these
    requests according to the action specified by the user"""

    req = request.get_json(force=True)
    action = req.get('result').get('action')
    res = None
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

    userSpecifiedData = req.get('result').get('contexts')[0].get('parameters')
    maxResults = int(userSpecifiedData.get('max-results'))
    totalResultsGiven = int(userSpecifiedData.get('total-results-given'))
    client = MovieDBApiClient(maxResults, totalResultsGiven)
    finalDiscoveryURL = MOVIE_DISCOVERY_URL
    # Get all filters specified by user on api.ai.
    userSpecifiedGenres = userSpecifiedData.get('genre')
    userSpecifiedCastFirstName = userSpecifiedData.get('cast-first-name')
    userSpecifiedCastLastName = userSpecifiedData.get('cast-last-name')
    # Chat agent only allows us to parse out first and last names seperately
    # so we need to merge these to get a list of full names.
    if len(userSpecifiedCastFirstName) == 0:
        userSpecifiedCast = []
    else:
        userSpecifiedCast = [s1 + " " + s2 for s1, s2 in zip(
            userSpecifiedCastFirstName, userSpecifiedCastLastName)]
        userSpecifiedCast = map(spellCheck, userSpecifiedCast)
    userSpecifiedRating = userSpecifiedData.get('rating')
    # Get movie database information using previously instantiated API client.
    genreIds = client.getGenresIds(userSpecifiedGenres)
    castIds = client.getCastIds(userSpecifiedCast)
    # Construct movie discovery URL.
    finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('with_genres', genreIds))
    finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('with_people', castIds))
    finalDiscoveryURL = finalDiscoveryURL + \
        client.encodeURLKeyValue(('certification', userSpecifiedRating))
    movies = client.getDiscoveredMovies(finalDiscoveryURL)
    movieDetails = client.getMovieDetails(movies)
    return prepareResponse(movies, movieDetails, "gathered-filters", maxResults + totalResultsGiven)

def processSimilarityRequest(req):
    """The function deals with processing a single movie provided by the user and
    returning a list of movies which are similar."""
    client = MovieDBApiClient()
    benchmarkMovie = req.get('result').get('contexts')[0].get('parameters').get('benchmark')
    benchmarkMovie = spellCheck(benchmarkMovie)
    similarMovies = client.getSimilarMovies(benchmarkMovie)
    movieDetails = client.getMovieDetails(similarMovies)
    return prepareResponse(similarMovies, movieDetails, "gathered-benchmark-movie")

def prepareResponse(movies, movieDetails, outboundContextName, outboundContextParam):
    """Helper function that prepares the return object we send to the user
     given a list of movies."""
    if len(movies) > 0:
        speech = "I found you the following movies: " + ', '.join(movies)
    else:
        speech = "Sorry, no movies available."
    return {
      "speech": speech,
      "displayText": speech,
      "source": "movie-recommendation-service",
      "contextOut" : [
          {"name" : outboundContextName, "parameters" : {"total-results-given" : outboundContextParam}, "lifespan" : 1 }
      ],
      "data" : movieDetails
    }

if __name__ == '__main__':
    app.run(debug=True, port=8888, host='0.0.0.0')
