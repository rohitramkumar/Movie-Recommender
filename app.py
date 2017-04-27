from flask import Flask, make_response, request, jsonify, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from webapi import web_api

import app_utils
import os
import json

# App and database config.
app = Flask(__name__)
app.register_blueprint(web_api)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/webhook', methods=['POST'])
def webhook():
    """Receives all requests from API.ai and processes these
    requests according to the action specified by the user."""

    req = request.get_json(force=True)
    action = req.get('result').get('action')
    res = None
    if action == "movie.filtering":
        res = process_filtering_request(req)
    elif action == "movie.similar":
        res = process_similarity_request(req)
    r = make_response(json.dumps(res))
    r.headers['Content-Type'] = 'application/json'
    return r


def process_filtering_request(req):
    """Deals with processing the movie filters provided by a user and feeding
    these filters into api calls for the movie database. The filtered movies
    returned from these api calls are returned to the user."""

    user_specified_data = req.get('result').get('contexts')[0].get('parameters')
    max_results = int(user_specified_data.get('max-results'))
    total_results_given = int(user_specified_data.get('total-results-given'))
    client = app_utils.MovieDBApiClient(max_results, total_results_given)
    final_discovery_url = app_utils.MOVIE_DISCOVERY_URL
    # Get all filters specified by user on api.ai.
    user_specified_genres = user_specified_data.get('genre')
    user_specified_cast_first_name = user_specified_data.get('cast-first-name')
    user_specified_cast_last_name = user_specified_data.get('cast-last-name')
    # Chat agent only allows us to parse out first and last names seperately
    # so we need to merge these to get a list of full names.
    if len(user_specified_cast_first_name) == 0 and len(user_specified_cast_last_name) == 0:
        user_specified_cast = []
    else:
        user_specified_cast = [s1 + " " + s2 for s1, s2 in zip(
            user_specified_cast_first_name, user_specified_cast_last_name)]
        user_specified_cast = map(app_utils.spell_check, user_specified_cast)
    user_specified_rating = user_specified_data.get('rating')
    # Get movie database information using previously instantiated API client.
    genre_ids = client.get_genre_ids(user_specified_genres)
    cast_ids = client.get_cast_ids(user_specified_cast)
    # Construct movie discovery URL.
    final_discovery_url = final_discovery_url + \
        client.encode_url_key_value(('with_genres', genre_ids))
    final_discovery_url = final_discovery_url + \
        client.encode_url_key_value(('with_people', cast_ids))
    final_discovery_url = final_discovery_url + \
        client.encode_url_key_value(('certification_country', 'US'))
    final_discovery_url = final_discovery_url + \
        client.encode_url_key_value(('certification', user_specified_rating))
    movies = client.get_discovered_movies(final_discovery_url)
    movie_details = client.get_movie_details(movies)
    return prepare_response(movies, movie_details, "gathered-filters", max_results + total_results_given)


def process_similarity_request(req):
    """Deals with processing a single movie provided by the user and returning
    a list of movies which are similar."""

    user_specified_data = req.get('result').get('contexts')[0].get('parameters')
    client = app_utils.MovieDBApiClient(0, 0)
    benchmarkMovie = user_specified_data.get('benchmark')
    benchmarkMovie = app_utils.spell_check(benchmarkMovie)
    similar_movies = client.get_similar_movies(benchmarkMovie)
    movie_details = client.get_movie_details(similar_movies)
    return prepare_response(similar_movies, movie_details, "gathered-benchmark-movie", 0)


def prepare_response(movies, movie_details, outbound_context_name, outbound_context_param):
    """Helper function that prepares the return object we send to the user
     given a list of movies."""

    if len(movies) > 0:
        speech = "I found you the following movies: " + ', '.join(movies) + ". Do you want more?"
    else:
        speech = "Sorry, no movies available."
    return {
        "speech": speech,
        "displayText": speech,
        "source": "movie-recommendation-service",
        "contextOut": [
            {
                "name": outbound_context_name,
                "parameters": {"total-results-given": outbound_context_param}, "lifespan": 1
            }
        ],
        "data": movie_details
    }

if __name__ == '__main__':
    # For local debugging.
    app.run(debug=True, port=8888, host='0.0.0.0')
