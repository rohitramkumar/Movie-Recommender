from flask import Flask, url_for, make_response, send_file, request, jsonify, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow

import os
import requests
import json
import datetime
import urllib
import sys
import logging
import api
import utils

app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)
# ma = Marshmallow(app)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

# Database that provides simple filtering.
MOVIE_DB_URL = 'https://api.themoviedb.org/3/'
API_KEY = os.environ['MOVIE_DB_API_KEY']

# URL Endpoints for different types of filtering data.
GENRES_URL = (MOVIE_DB_URL + 'genre/movie/list?api_key={}&language=en-US').format(API_KEY)
PEOPLE_SEARCH_URL = (
    MOVIE_DB_URL + 'search/person/?api_key={}&language=en-US&query={}&page1&include_adult=false')

# URL Endpoint for movie discovery
MOVIE_DISCOVERY_URL = (
    MOVIE_DB_URL + 'discover/movie?api_key={}&include_adult=false&include_video=false&language=en-US&sort_by=popularity.desc').format(API_KEY)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/login/", methods=['POST'])
def get_user():
    user_detail = json.loads(request.data)

    username = user_detail.get("username")
    password = user_detail.get("password")

    return jsonify(api.login(username, password))


@app.route("/api/signup/", methods=['POST'])
def add_user():
    """This function triggers an API call to add a new
    user into the database"""
    new_user = json.loads(request.data)

    first_name = new_user.get("firstname")
    last_name = new_user.get("lastname")
    username = new_user.get("username")
    password = new_user.get("password")

    return api.create_user(username, password, first_name, last_name)


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

    client = MovieDBApiClient()
    finalDiscoveryURL = MOVIE_DISCOVERY_URL
    userSpecifiedData = req.get('result').get('contexts')[0]
    # Get all filters specified by user on api.ai.
    userSpecifiedGenres = userSpecifiedData.get('parameters').get('genre')
    userSpecifiedCastFirstName = userSpecifiedData.get('parameters').get('cast-first-name')
    userSpecifiedCastLastName = userSpecifiedData.get('parameters').get('cast-last-name')
    # Chat agent only allows us to parse out first and last names seperately
    # so we need to merge these to get a list of full names.
    if len(userSpecifiedCastFirstName) == 0:
        userSpecifiedCast = []
    else:
        userSpecifiedCast = [s1 + " " + s2 for s1, s2 in zip(
            userSpecifiedCastFirstName, userSpecifiedCastLastName)]
        userSpecifiedCast = map(spellCheck, userSpecifiedCast)
    userSpecifiedRating = userSpecifiedData.get('parameters').get('rating')
    # Get movie database information using previously instantiated API client.
    genreIds = client.getGenresIds(userSpecifiedGenres)
    castIds = client.getCastIds(userSpecifiedCast)
    # Construct movie discovery URL.
    finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('with_genres', genreIds))
    finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('with_people', castIds))
    finalDiscoveryURL = finalDiscoveryURL + \
        client.encodeURLKeyValue(('certification', userSpecifiedRating))
    movies = client.getDiscoveredMovies(finalDiscoveryURL)
    return prepareResponse(movies)


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
        "speech": speech,
      "displayText": speech,      "source": "movie-recommendation-service"
    }

if __name__ == '__main__':
    app.run(debug=True, port=8888, host='0.0.0.0')
