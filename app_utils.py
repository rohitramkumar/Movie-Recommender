import requests
import json
import urllib
import os

# API Keys
BING_SC_API_KEY = os.environ['BING_SC_API_KEY']
MOVIE_DB_API_KEY = os.environ['MOVIE_DB_API_KEY']
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
