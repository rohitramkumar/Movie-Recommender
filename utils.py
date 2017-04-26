import requests
import json
import urllib
import os
import model
import time

# API Keys
GUIDEBOX_API_KEY = os.environ['GUIDEBOX_API_KEY']
BING_SC_API_KEY = os.environ['BING_SC_API_KEY']
MOVIE_DB_API_KEY = os.environ['MOVIE_DB_API_KEY']
# URL endpoint which provides a guidebox movie id
GUIDEBOX_MOVIE_SEARCH_URL = 'http://api-public.guidebox.com/v2/search?api_key={}&type=movie&field=title&query={}'
# URL endpoint which provides info about a movie given a guidebox id
GUIDEBOX_MOVIE_INFO_URL = 'http://api-public.guidebox.com/v2/movies/{}?api_key={}'
# Movie database that provides simple filtering
MOVIE_DB_URL = 'https://api.themoviedb.org/3/'
# URL Endpoints for different types of filtering data
GENRES_URL = (
    MOVIE_DB_URL +
    'genre/movie/list?api_key={}&language=en-US').format(MOVIE_DB_API_KEY)
PEOPLE_SEARCH_URL = (
    MOVIE_DB_URL +
    'search/person?api_key={}&language=en-US&query={}&page=1&include_adult=false')
MOVIE_SEARCH_URL = (
    MOVIE_DB_URL +
    'search/movie?api_key={}&language=en-US&query={}&page=1&include_adult=false')
# URL Endpoint for movie discovery
MOVIE_DISCOVERY_URL = (
    MOVIE_DB_URL +
    'discover/movie?api_key={}&include_adult=false&include_video=false&language=en-US&sort_by=popularity.desc').format(MOVIE_DB_API_KEY)
# URL Endpoint for movie similarity
MOVIE_SIMILARITY_URL = (
    MOVIE_DB_URL +
    'movie/{}/similar?api_key={}&language=en-US')
# URL Endpoint for movie info
MOVIE_INFO_URL = (MOVIE_DB_URL + 'movie/{}?api_key={}&language=en-US')
# URL Endpoint for movie info (credits)
MOVIE_CREDITS_URL = (MOVIE_DB_URL + 'movie/{}/credits?api_key={}')
# URL Endpoint for fetching movie posters
MOVIE_POSTER_URL = 'https://image.tmdb.org/t/p/w185/'
# URL Endpoint for spell checking
BING_SC_URL = 'https://api.cognitive.microsoft.com/bing/v5.0/spellcheck/?mode=proof&mkt=en-us'
# Learning Agent recommendation URL
LEARNING_AGENT_REC_URL = "https://52.165.149.158/mrelearner/api/v1.0/recommender"
# Learning Agent history URL
LEARNING_AGENT_HIST_URL = "https://52.165.149.158/mrelearner/api/v1.0/history"
# Max possible number of results that can be returned
MAX_RESULTS = 10


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


def spell_check(query):
    """Given a potentially misspelled query, return the correct spelling with
    the proper punctuation, capitalization, etc if necessary. Uses the Bing
    Spell Check API."""

    new_query = query
    encoded_query = urllib.quote_plus(query)
    url = BING_SC_URL + '&text=' + encoded_query
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Ocp-Apim-Subscription-Key': BING_SC_API_KEY}
    spell_check_response = requests.post(url, headers=headers)
    spell_check_info = json.loads(spell_check_response.text)
    for flagged_token in spell_check_info.get('flaggedTokens'):
        token = flagged_token.get('token')
        suggestion = flagged_token.get('suggestions')[0].get('suggestion')
        new_query = new_query.replace(token, suggestion)
    return new_query


def get_guidebox_info(movie_names):
    """Given a list of movie names, return the Guidebox information for each.
    Guidebox provides metacritic links and links to streaming services."""

    guidebox_info = {}
    for movie in movie_names:
        movie_id_result = requests.get(
            GUIDEBOX_MOVIE_SEARCH_URL.format(
                GUIDEBOX_API_KEY, movie)).json()
        if len(movie_id_result.get('results')) == 0:
            guidebox_info[movie] = "No info"
            continue
        movie_id = movie_id_result.get('results')[0].get('id')
        guidebox_info_result = requests.get(
            GUIDEBOX_MOVIE_INFO_URL.format(
                movie_id, GUIDEBOX_API_KEY)).json()
        # If the movie is in theaters, then provide the fandango link and the
        # metacritic link.
        if guidebox_info_result.get('in_theaters') is True:
            fandango = None
            other_sources = guidebox_info_result.get('other_sources')
            if 'movie_theater' in other_sources:
                for source in other_sources:
                    if source.get('source') == 'fandango':
                        fandango = source.get('link')
                        guidebox_info[movie] = {
                            'metacritic': guidebox_info_result.get('metacritic'),
                            'fandango': fandango}
            else:
                guidebox_info[movie] = {
                    'metacritic': guidebox_info_result.get('metacritic')}
        # If the movie is not in theatres, provide the metacritic link and a
        # list of streaming options, if applicable.
        else:
            subscription_web_sources = guidebox_info_result.get(
                'subscription_web_sources')
            streaming = []
            for source in subscription_web_sources:
                streaming.append({'source': source.get(
                    'source'), 'link': source.get('link')})
            purchase_web_sources = guidebox_info_result.get(
                'purchase_web_sources')
            for source in purchase_web_sources:
                streaming.append({'source': source.get(
                    'source'), 'link': source.get('link')})
            guidebox_info[movie] = {
                'metacritic': guidebox_info_result.get('metacritic'),
                'streaming': streaming}
    return guidebox_info


class MovieDBApiClient:

    """This class abstracts API calls for the api.themoviedb.org."""

    def __init__(self, max_results, offset):
        self.max_results = max_results if max_results > 0 and max_results < MAX_RESULTS else MAX_RESULTS
        self.offset = offset

    def get_movie_details(self, movie_list):
        """Gets the imdb id, cast, title, overview and picture for each movie."""
        movie_ids = []
        for movie in movie_list:
            movie_id_result = requests.get(
                MOVIE_SEARCH_URL.format(
                    MOVIE_DB_API_KEY,
                    urllib.quote_plus(movie)))
            movie_id_info = json.loads(movie_id_result.text)
            if len(movie_id_info.get('results')) > 0:
                movie_id = movie_id_info.get('results')[0].get('id')
                movie_ids.append(movie_id)
        full_movie_details = []
        counter = 0
        for movie_id in movie_ids:
            full_movie_details.append({})
            movie_info_result = requests.get(
                MOVIE_INFO_URL.format(
                    movie_id, MOVIE_DB_API_KEY))
            cast_info_result = requests.get(
                MOVIE_CREDITS_URL.format(
                    movie_id, MOVIE_DB_API_KEY))
            movie_info = json.loads(movie_info_result.text)
            cast_info = json.loads(cast_info_result.text)
            imdb_id_str = movie_info['imdb_id'][2:]
            full_movie_details[counter]['imdb_id'] = imdb_id_str
            full_movie_details[counter]['overview'] = movie_info['overview']
            full_movie_details[counter]['original_title'] = movie_info['original_title']
            full_movie_details[counter]['poster'] = MOVIE_POSTER_URL + \
                movie_info['poster_path']
            full_movie_details[counter]['cast'] = [item['name']
                                                   for item in cast_info['cast'][:5]]
            full_movie_details[counter]['release_date'] = movie_info['release_date']
            counter += 1
        return full_movie_details

    def get_genre_ids(self, user_specified_genres):
        """Gets a list of genre id's corresponding to the names of the genres
        specified by the user."""

        genre_request_result = requests.get(GENRES_URL)
        genres = json.loads(genre_request_result.text)
        # For each user specified genre, find its corresponding genre id
        genre_ids = []
        for user_specified_genre in user_specified_genres:
            for genre in genres['genres']:
                if user_specified_genre == genre['name']:
                    genre_ids.append(genre['id'])
        return genre_ids

    def get_cast_ids(self, user_specified_cast):
        """Gets a list of cast (actor) id's corresponding to the names of the
        cast specified by the user."""

        cast_ids = []
        for cast in user_specified_cast:
            cast_request_result = requests.get(
                PEOPLE_SEARCH_URL.format(
                    MOVIE_DB_API_KEY,
                    urllib.quote_plus(cast)))
            cast_info = json.loads(cast_request_result.text)
            if len(cast_info.get('results')) > 0:
                cast_ids.append(cast_info.get('results')[0].get('id'))
        return cast_ids

    def get_discovered_movies(self, discovery_url):
        """Given an API endpoint which corresponds to movie discovery given a set
        of filters, get a list of movies that are returned."""

        movie_discovery_result = requests.get(discovery_url)
        movie_info = json.loads(movie_discovery_result.text)
        movies = []
        counter = 0
        while counter < self.max_results and counter + \
                self.offset < len(movie_info.get('results')):
            movies.append(
                movie_info.get('results')[
                    counter +
                    self.offset].get('title'))
            counter += 1
        return movies

    def get_similar_movies(self, benchmark_movie):
        """Given a benchmark movie, return a list of movies that are similar."""

        similar_movies = []
        # First, get the id of the movie given the name.
        benchmark_movie_id_result = requests.get(
            MOVIE_SEARCH_URL.format(
                MOVIE_DB_API_KEY,
                urllib.quote_plus(benchmark_movie)))
        benchmark_movie_id_info = json.loads(benchmark_movie_id_result.text)
        if len(benchmark_movie_id_info.get('results')) > 0:
            benchmark_movie_id = benchmark_movie_id_info.get('results')[
                0].get('id')
            # Get the similar movies given the movie id.
            movie_similarity_request = requests.get(
                MOVIE_SIMILARITY_URL.format(
                    benchmark_movie_id, MOVIE_DB_API_KEY))
            movie_similarity_info = json.loads(movie_similarity_request.text)
            if len(movie_similarity_info.get('results')) > 0:
                similar_movies.append(
                    movie_similarity_info.get('results')[0].get('title'))
        return similar_movies

    def encode_url_key_value(self, pair):
        """Takes a tuple consisting of a key and a value and encodes it in a format
        that is acceptable for a url string. This is useful for appending
        parameters and their values to an API url."""
        if len(pair[1]) == 0 or len(pair[0]) == 0:
            return ""
        else:
            if isinstance(pair[1], list):
                return '&' + pair[0] + '=' + ','.join(str(i) for i in pair[1])
            else:
                return '&' + pair[0] + '=' + pair[1]


class LearningAgentClient:

    """This class abstracts API calls to our learning agent on Azure."""

    def get_recommended_movies(self, data):
        result = requests.post(LEARNING_AGENT_REC_URL, json=data, auth=(
            "movierecommender", "vast_seas_of_infinity"), verify=False)
        return result.json()

    def add_movie_to_user_history(self, data):
        requests.post(LEARNING_AGENT_HIST_URL, json=data, auth=(
            "movierecommender", "vast_seas_of_infinity"), verify=False)
