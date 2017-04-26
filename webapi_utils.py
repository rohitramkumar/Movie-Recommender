import model
import time
import os
import requests

# API Keys
GUIDEBOX_API_KEY = os.environ['GUIDEBOX_API_KEY']
# URL endpoint which provides a guidebox movie id
GUIDEBOX_MOVIE_SEARCH_URL = 'http://api-public.guidebox.com/v2/search?api_key={}&type=movie&field=title&query={}'
# URL endpoint which provides info about a movie given a guidebox id
GUIDEBOX_MOVIE_INFO_URL = 'http://api-public.guidebox.com/v2/movies/{}?api_key={}'


def create_user(username, password, first_name, last_name):
    """Used for sign-up. Gets form data and adds new user to users table."""

    if not password:
        return "Cannot leave password empty"
    if not first_name:
        return "Cannot have first name empty"
    # Check if user exists
    user = model.User.query.filter_by(email=username).first()
    # If user doesn't exist, create user
    if user is None:
        user = model.User(email=username, password=password,
                          first_name=first_name, last_name=last_name)
        model.session.add(user)
        model.session.commit()
        return "Success"
    return "Username already exits"


def login(username, password):
    """Used for login. Check if user exists; if exists,
    authenticates credentials and returns success message."""

    user = model.User.query.filter_by(email=username).first()
    if user:
        if user.password == password:
            return user.as_dict()
    return "Fail"


def get_watchlist(username):
    """Returns all movies in a user's watchlist"""

    user = model.User.query.filter_by(email=username).first()
    if not user:
        return "Fail"
    movie_list = []
    for movie in user.movies:
        movie_list.append(movie.as_dict())
    return movie_list


def add_movie_to_watchlist(
        username,
        user_id,
        movie_name,
        movie_imdb_id,
        movie_rating):
    """Check if user exists; if exists, add movie to specified user's watchlist.
    Also add movie to learning agent database"""

    user = model.User.query.filter_by(email=username).first()
    if not user:
        return "Fail: Cannot find user!"
    new_movie = model.Movie(
        name=movie_name,
        movie_imdb_id=movie_imdb_id,
        user_rating=movie_rating)
    for movie in user.movies:
        if movie.name == movie_name:
            return "Movie already present in watchlist!"
    user.movies.append(new_movie)
    model.session.commit()
    # Learning Agent watchlist.
    client = LearningAgentClient()
    client.add_movie_to_user_history({'user_id': user_id,
                                      'movie_imdb_id': movie_imdb_id,
                                      'user_rating': movie_rating,
                                      'timestamp': int(time.time())})
    return "Success"


def get_guidebox_info(movie_names):
    """Given a list of movie names, return the Guidebox information for each.
    Guidebox provides metacritic links and links to streaming services."""
    guidebox_info = {}
    for movie in movie_names:
        movie_id_result = requests.get(
            GUIDEBOX_MOVIE_SEARCH_URL.format(GUIDEBOX_API_KEY, movie)).json()
        if len(movie_id_result.get('results')) == 0:
            guidebox_info[movie] = "No info"
            continue
        movie_id = movie_id_result.get('results')[0].get('id')
        guidebox_info_result = requests.get(
            GUIDEBOX_MOVIE_INFO_URL.format(movie_id, GUIDEBOX_API_KEY)).json()
        # If the movie is in theaters, then provide the fandango link and the metacritic link.
        if guidebox_info_result.get('in_theaters') == True:
            fandango = None
            other_sources = guidebox_info_result.get('other_sources').get('movie_theater')
            for source in other_sources:
                if source.get('source') == 'fandango':
                    fandango = source.get('link')
            guidebox_info[movie] = {
                'metacritic': guidebox_info_result.get('metacritic'), 'fandango': fandango}
        # If the movie is not in theatres, provide the metacritic link and a list
        # of streaming options, if applicable.
        else:
            subscription_web_sources = guidebox_info_result.get('subscription_web_sources')
            streaming = []
            for source in subscription_web_sources:
                streaming.append({'source': source.get('source'), 'link': source.get('link')})
            purchase_web_sources = guidebox_info_result.get('purchase_web_sources')
            for source in purchase_web_sources:
                streaming.append({'source': source.get('source'), 'link': source.get('link')})
            guidebox_info[movie] = {
                'metacritic': guidebox_info_result.get('metacritic'), 'streaming': streaming}
return guidebox_info
