from flask import Blueprint, jsonify, request

import webapi_utils
import json

web_api = Blueprint('web_api', __name__)

@web_api.route("/api/login/", methods=['POST'])
def login():
    """API endpoint which handles login authentication for the frontend."""

    user_detail = json.loads(request.data)
    username = user_detail.get("username")
    password = user_detail.get("password")
    return jsonify(webapi_utils.login(username, password))


@web_api.route("/api/signup/", methods=['POST'])
def signup():
    """API endpoint which handles user signup."""

    new_user = json.loads(request.data)
    first_name = new_user.get("firstname")
    last_name = new_user.get("lastname")
    username = new_user.get("username")
    password = new_user.get("password")
    return webapi_utils.create_user(username, password, first_name, last_name)


@web_api.route("/api/add_movie_to_watchlist/", methods=['POST'])
def add_movie_to_watchlist():
    """API endpoint which adds a new movie into the watchlist for a user."""

    movie_detail = json.loads(request.data)
    username = movie_detail.get("username")
    user_id = movie_detail.get("user_id")
    movie_name = movie_detail.get("movieName")
    movie_imdb_id = movie_detail.get("movieImdbId")
    movie_rating = movie_detail.get("rating")
    return webapi_utils.add_movie_to_watchlist(username, user_id, movie_name, movie_imdb_id, movie_rating)

@web_api.route("/api/get_watchlist/", methods=['POST'])
def get_watchlist():
    """API endpoint which gets all movies in a user's watchlist."""

    user_id = request.data
    return jsonify(webapi_utils.get_watchlist(user_id))

@web_api.route("/api/get_learning_recommendation/", methods=['POST'])
def get_learning_recommendation():
    """API endpoint which gets a movie recommendation based on a user's watchlist."""

    req = json.loads(request.data)
    data = {"user_id": req.get("user_id"), "candidate_list": req.get("candidateList")}
    client = webapi_utils.LearningAgentClient()
    result = client.get_recommended_movies(data)
    if result['result'] == []:
        return jsonify("Watchlist is empty so no recommendation can be made")
    else:
        return jsonify(result['result'])

@web_api.route("/api/get_guidebox_info/", methods=['POST'])
def get_guidebox_info():
    """"API endpoint which gets more movie information from Guidebox."""

    req = json.loads(request.data)
    movie_names = req.get('movieNames')
    guidebox_info = webapi_utils.get_guidebox_info(movie_names)
    return jsonify(guidebox_info)
