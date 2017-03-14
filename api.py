import model
import json
"""Sign-up"""


def create_user(username, password, first_name, last_name):
    """Get form data and add new user to users table"""

    if not password:
        return "Cannot leave password empty"
    if not first_name:
        return "Cannot have first name empty"

    # Check if user exists
    user = model.User.query.filter_by(email=username).first()

    # If user doesn't exist, create user
    if user == None:
        user = model.User(email=username,
                          password=password, first_name=first_name, last_name=last_name)
        model.session.add(user)
        model.session.commit()

        return "Success"

    return "Username already exits"


def login(username, password):
    """Check if user exists; if exists, authenticate pw and return success msg"""

    user = model.User.query.filter_by(email=username).first()

    if user:
        if user.password == password:
            # myUser = {"username": user.user['email'], "password": user.user[
            #    'password'], "firstname": user.user['first_name'], "lastname": user.user['last_name']}
            return user.as_dict()

    return "Fail"


def get_movie_all(username):
    """Check if user exists and return all movies in watchlist"""

    user = model.User.query.filter_by(email=username).first()

    if not user:
        return "Fail"

    movie_list = []

    for movie in user.movies:
        movie_list.append(movie.as_dict())

    return movie_list


def add_movie(username, movieName, movieImdbId, movieRating):
    """Check if user exists; if exists, authenticate pw and return success msg"""

    user = model.User.query.filter_by(email=username).first()

    if not user:
        return "Fail: Cannot find user!"

    newMovie = model.Movie(name=movieName, movie_imdb_id=movieImdbId, user_rating=movieRating)

    for movie in user.movies:
        print movie
        if int(movie.movie_imdb_id) == int(movieImdbId):
            return "Movie already present in watchlist!"

    user.movies.append(newMovie)
    model.session.commit()

    return "Success"
