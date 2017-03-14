from flask import Flask, url_for, make_response, send_file, request, jsonify, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow

import utils
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
    return jsonify(utils.login(username, password))


@app.route("/api/signup/", methods=['POST'])
def signup():
    new_user = json.loads(request.data)
    first_name = new_user.get("firstname")
    last_name = new_user.get("lastname")
    username = new_user.get("username")
    password = new_user.get("password")
    return utils.createUser(username, password, first_name, last_name)


@app.route("/api/add_movie/", methods=['POST'])
def add_movie():
    """This function triggers an API call to add a new
    movie into the watchlist for a user"""
    movie_detail = json.loads(request.data)

    username = movie_detail.get("username")
    movieName = movie_detail.get("movieName")
    movieImdbID = movie_detail.get("movieImdbId")
    movieRating = movie_detail.get("movieRating")

    return utils.add_movie(username, movieName, movieImdbID, movieRating)


@app.route("/api/get_movie_all/", methods=['POST'])
def get_all_movies():
    """This function triggers an API call to add a new
    movie into the watchlist for a user"""
    user_id = request.data

    return jsonify(utils.get_movie_all(user_id))


@app.route("/api/getFullMovieDetails", methods=['POST'])
def getFullMovieDetails():
    """ Get the imdb id, cast, title, and picture for each of the movies given.
    Also query the learning agent for the history-based recommendation."""
    print 'I was entered'

    req = request.get_json(force=True)
    print req

    ai = apiai.ApiAI(utils.APIAI_KEY)
    movieDBClient = utils.MovieDBApiClient(0, 0)
    eventRequest = ai.event_request(apiai.events.Event("get-full-movie-data-event"))
    eventResponse = eventRequest.getresponse()
    apiaiData = json.loads(eventResponse.read())
    contextData = apiaiData['result']['contexts'][0]['parameters']
    movieList = contextData['returned-movie-list']
    fullMovieDetails = movieDBClient.getMovieDetails(movieList)
    print contextData
    print fullMovieDetails
    print 'Exiting'

    return jsonify(fullMovieDetails)


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
    client = utils.MovieDBApiClient(maxResults, totalResultsGiven)
    finalDiscoveryURL = utils.MOVIE_DISCOVERY_URL
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
        userSpecifiedCast = map(utils.spellCheck, userSpecifiedCast)
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
    return prepareResponse(movies, "gathered-filters", maxResults + totalResultsGiven)


def processSimilarityRequest(req):
    """The function deals with processing a single movie provided by the user and
    returning a list of movies which are similar."""
    client = utils.MovieDBApiClient()
    benchmarkMovie = req.get('result').get('contexts')[0].get('parameters').get('benchmark')
    benchmarkMovie = utils.spellCheck(benchmarkMovie)
    similarMovies = client.getSimilarMovies(benchmarkMovie)
    return prepareResponse(similarMovies, "gathered-benchmark-movie")


def prepareResponse(movies, outboundContextName, outboundContextParam):
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
      "contextOut": [
          {"name": outboundContextName, "parameters": {"total-results-given":
           outboundContextParam, "returned-movie-list": movies}, "lifespan": 1}
      ]
    }

if __name__ == '__main__':
    app.run(debug=True, port=8888, host='0.0.0.0')
