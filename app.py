from flask import Flask, url_for, make_response, send_file, request, jsonify, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

import utils
import apiai
import os
import requests
import json
import sys
import logging

# App and database config.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
Bootstrap(app)
db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/login/", methods=['POST'])
def login():
    """API endpoint which handles login authentication for the frontend."""

    user_detail = json.loads(request.data)
    username = user_detail.get("username")
    password = user_detail.get("password")

    return jsonify(utils.login(username, password))


@app.route("/api/signup/", methods=['POST'])
def signup():
    """API endpoint which handles user signup."""

    new_user = json.loads(request.data)
    first_name = new_user.get("firstname")
    last_name = new_user.get("lastname")
    username = new_user.get("username")
    password = new_user.get("password")

    return utils.createUser(username, password, first_name, last_name)


@app.route("/api/add_movie_to_watchlist/", methods=['POST'])
def add_movie_to_watchlist():
    """API endpoint which adds a new movie into the watchlist for a user."""

    movie_detail = json.loads(request.data)
    username = movie_detail.get("username")
    user_id = movie_detail.get("user_id")
    movie_name = movie_detail.get("movieName")
    movie_imdb_id = movie_detail.get("movieImdbId")
    movie_rating = movie_detail.get("rating")
    return utils.add_movie_to_watchlist(username, user_id, movie_name, movie_imdb_id, movie_rating)

@app.route("/api/get_watchlist/", methods=['POST'])
def get_watchlist():
    """API endpoint which gets all movies in a user's watchlist."""

    user_id = request.data
    return jsonify(utils.get_watchlist(user_id))

@app.route("/api/get_learning_recommendation/", methods=['POST'])
def get_learning_recommendation():
    """API endpoint which gets a movie recommendation based on a user's watchlist."""
    req = json.loads(request.data)
    data = {"user_id": req.get("user_id"), "candidate_list": req.get("candidateList")}
    client = utils.LearningAgentClient()
    result = client.getRecommendedMovies(data)
    if result['result'] == []:
        return jsonify("Watchlist is empty so no recommendation can be made")
    else:
        return jsonify(result['result'])

@app.route("/api/get_showtimes/", methods=['POST'])
def get_showtimes():
    """"API endpoint which gets showtimes for a movie given the user's location."""
    req = json.loads(request.data)
    movie_name = req.get("name")
    coordinates = {'lat' : req.get('lat'), 'lng' : req.get('lng')}
    showtimes = utils.get_showtimes(movie_name, coordinates)
    return jsonify(showtimes)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receives all requests from API.ai and processes these
    requests according to the action specified by the user."""

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
    """Deals with processing the movie filters provided by a user and feeding
    these filters into api calls for the movie database. The filtered movies
    returned from these api calls are returned to the user."""

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
    if len(userSpecifiedCastFirstName) == 0 and len(userSpecifiedCastLastName) == 0:
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
    print(userSpecifiedRating)
    finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('with_genres', genreIds))
    finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('with_people', castIds))
    finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('certification_country', 'US'))
    finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('certification', userSpecifiedRating))
    print(finalDiscoveryURL)
    movies = client.getDiscoveredMovies(finalDiscoveryURL)
    movieDetails = client.getMovieDetails(movies)
    return prepareResponse(movies, movieDetails, "gathered-filters", maxResults + totalResultsGiven)


def processSimilarityRequest(req):
    """Deals with processing a single movie provided by the user and returning
    a list of movies which are similar."""

    userSpecifiedData = req.get('result').get('contexts')[0].get('parameters')
    client = utils.MovieDBApiClient(0, 0)
    benchmarkMovie = userSpecifiedData.get('benchmark')
    benchmarkMovie = utils.spellCheck(benchmarkMovie)
    similarMovies = client.getSimilarMovies(benchmarkMovie)
    movieDetails = client.getMovieDetails(similarMovies)
    return prepareResponse(similarMovies, movieDetails, "gathered-benchmark-movie", 0)

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
        "contextOut": [
            {
                "name": outboundContextName,
                "parameters": {"total-results-given": outboundContextParam}, "lifespan": 1
            }
        ],
        "data": movieDetails
    }

if __name__ == '__main__':
    # For local debugging.
    app.run(debug=True, port=8888, host='0.0.0.0')
