import requests
import json
import urllib
import os
import model
import time

APIAI_KEY = 'd9854338952446d589f83e6a575e0ba4'
BING_SC_API_KEY = '1c964897dce84d8cb04b5e8ff4634d48'
MOVIE_DB_API_KEY = '207c3617b856ea5adac5ff6ad68b0bb7'
# Database that provides simple filtering.
MOVIE_DB_URL = 'https://api.themoviedb.org/3/'
# URL Endpoints for different types of filtering data.
GENRES_URL = (MOVIE_DB_URL + 'genre/movie/list?api_key={}&language=en-US').format(MOVIE_DB_API_KEY)
PEOPLE_SEARCH_URL = (
    MOVIE_DB_URL + 'search/person?api_key={}&language=en-US&query={}&page=1&include_adult=false')
MOVIE_SEARCH_URL = (
    MOVIE_DB_URL + 'search/movie?api_key={}&language=en-US&query={}&page=1&include_adult=false')
# URL Endpoint for movie discovery
MOVIE_DISCOVERY_URL = (
    MOVIE_DB_URL + 'discover/movie?api_key={}&include_adult=false&include_video=false&language=en-US&sort_by=popularity.desc').format(MOVIE_DB_API_KEY)
# URL Endpoint for movie similarity
MOVIE_SIMILARITY_URL = (MOVIE_DB_URL + 'movie/{}/similar?api_key={}&language=en-US')
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


def createUser(username, password, first_name, last_name):
    """Used for sign-up. Gets form data and adds new user to users table"""

    if not password:
        return "Cannot leave password empty"
    if not first_name:
        return "Cannot have first name empty"
    # Check if user exists
    user = model.User.query.filter_by(email=username).first()
    # If user doesn't exist, create user
    if user == None:
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


def add_movie_to_watchlist(username, userID, movieName, movieImdbId, movieRating):
    """Check if user exists; if exists, add movie to specified user's watchlist.
    Also add movie to learning agent database"""

    user = model.User.query.filter_by(email=username).first()
    if not user:
        return "Fail: Cannot find user!"
    newMovie = model.Movie(name=movieName, movie_imdb_id=movieImdbId, user_rating=movieRating)
    for movie in user.movies:
        if movie.name == movieName:
            return "Movie already present in watchlist!"
    user.movies.append(newMovie)
    model.session.commit()
    # Learning Agent watchlist.
    client = LearningAgentClient()
    client.addMovieToUserHistory({'user_id': userID,
                                  'movie_imdb_id': movieImdbId,
                                  'user_rating': movieRating,
                                  'timestamp': int(time.time())})
    return "Success"


def spellCheck(query):
    """Given a potentially misspelled query, return the correct spelling with
    the proper punctuation, capitalization, etc if necessary. Uses the Bing
    Spell Check API."""

    newQuery = query
    encodedQuery = urllib.quote_plus(query)
    url = BING_SC_URL + '&text=' + encodedQuery
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Ocp-Apim-Subscription-Key': '1c964897dce84d8cb04b5e8ff4634d48'}
    spellCheckResponse = requests.post(url, headers=headers)
    spellCheckInfo = json.loads(spellCheckResponse.text)
    for flaggedToken in spellCheckInfo.get('flaggedTokens'):
        token = flaggedToken.get('token')
        suggestion = flaggedToken.get('suggestions')[0].get('suggestion')
        newQuery = newQuery.replace(token, suggestion)
    return newQuery


class MovieDBApiClient:

    """This class abstracts API calls for the api.themoviedb.org."""

    def __init__(self, maxResults, offset):
        self.maxResults = maxResults if maxResults > 0 and maxResults < MAX_RESULTS else MAX_RESULTS
        self.offset = offset

    def getMovieDetails(self, movieList):
        """Gets the imdb id, cast, title, overview and picture for each movie."""
        movieIds = []
        for movie in movieList:
            movieIdResult = requests.get(
                MOVIE_SEARCH_URL.format(MOVIE_DB_API_KEY, urllib.quote_plus(movie)))
            movieIdInfo = json.loads(movieIdResult.text)
            if len(movieIdInfo.get('results')) > 0:
                movieId = movieIdInfo.get('results')[0].get('id')
                movieIds.append(movieId)
        fullMovieDetails = []
        counter = 0
        for movieId in movieIds:
            fullMovieDetails.append({})
            movieInfoResult = requests.get(MOVIE_INFO_URL.format(movieId, MOVIE_DB_API_KEY))
            castInfoResult = requests.get(MOVIE_CREDITS_URL.format(movieId, MOVIE_DB_API_KEY))
            movieInfo = json.loads(movieInfoResult.text)
            castInfo = json.loads(castInfoResult.text)
            imdb_id_str = movieInfo['imdb_id'][2:]
            fullMovieDetails[counter]['imdb_id'] = imdb_id_str
            fullMovieDetails[counter]['overview'] = movieInfo['overview']
            fullMovieDetails[counter]['original_title'] = movieInfo['original_title']
            fullMovieDetails[counter]['poster'] = MOVIE_POSTER_URL + movieInfo['poster_path']
            fullMovieDetails[counter]['cast'] = [item['name'] for item in castInfo['cast'][:5]]
            fullMovieDetails[counter]['release_date'] = movieInfo['release_date']
            counter += 1
        return fullMovieDetails

    def getGenresIds(self, userSpecifiedGenres):
        """Gets a list of genre id's corresponding to the names of the genres
        specified by the user."""

        genreRequestResult = requests.get(GENRES_URL)
        genres = json.loads(genreRequestResult.text)
        # For each user specified genre, find its corresponding genre id
        genreIds = []
        for userSpecifiedGenre in userSpecifiedGenres:
            for genre in genres['genres']:
                if userSpecifiedGenre == genre['name']:
                    genreIds.append(genre['id'])
        return genreIds

    def getCastIds(self, userSpecifiedCast):
        """Gets a list of cast (actor) id's corresponding to the names of the
        cast specified by the user."""

        castIds = []
        for cast in userSpecifiedCast:
            castRequestResult = requests.get(
                PEOPLE_SEARCH_URL.format(MOVIE_DB_API_KEY, urllib.quote_plus(cast)))
            castInfo = json.loads(castRequestResult.text)
            if len(castInfo.get('results')) > 0:
                castIds.append(castInfo.get('results')[0].get('id'))
        return castIds

    def getDiscoveredMovies(self, discoveryURL):
        """Given an API endpoint which corresponds to movie discovery given a set
        of filters, get a list of movies that are returned."""

        movieDiscoveryResult = requests.get(discoveryURL)
        movieInfo = json.loads(movieDiscoveryResult.text)
        movies = []
        counter = 0
        while counter < self.maxResults and counter + self.offset < len(movieInfo.get('results')):
            movies.append(movieInfo.get('results')[counter + self.offset].get('title'))
            counter += 1
        return movies

    def getSimilarMovies(self, benchmarkMovie):
        """Given a benchmark movie, return a list of movies that are similar."""

        similarMovies = []
        # First, get the id of the movie given the name.
        benchmarkMovieIdResult = requests.get(
            MOVIE_SEARCH_URL.format(MOVIE_DB_API_KEY, urllib.quote_plus(benchmarkMovie)))
        benchmarkMovieIdInfo = json.loads(benchmarkMovieIdResult.text)
        if len(benchmarkMovieIdInfo.get('results')) > 0:
            benchmarkMovieId = benchmarkMovieIdInfo.get('results')[0].get('id')
            # Get the similar movies given the movie id.
            movieSimilarityResult = requests.get(
                MOVIE_SIMILARITY_URL.format(benchmarkMovieId, MOVIE_DB_API_KEY))
            movieSimilarityInfo = json.loads(movieSimilarityResult.text)
            if len(movieSimilarityInfo.get('results')) > 0:
                similarMovies.append(movieSimilarityInfo.get('results')[0].get('title'))
        return similarMovies

    def encodeURLKeyValue(self, pair):
        """Takes a tuple consisting of a key and a value and encodes it in a format
        that is acceptable for a url string. This is useful for appending
        parameters and their values to an API url."""

        if len(pair[1]) == 0 or len(pair[0]) == 0:
            return ""
        else:
            if type(pair[1]) == list:
                return '&' + pair[0] + '=' + ''.join(str(i) for i in pair[1])
            elif type(pair[1]) == str:
                return '&' + pair[0] + '=' + pair[1]
            else:
                return ""


class LearningAgentClient:

    """This class abstracts API calls to our learning agent on Azure."""

    def getRecommendedMovies(self, data):
        result = requests.post(LEARNING_AGENT_REC_URL, json=data, auth=(
            "movierecommender", "vast_seas_of_infinity"), verify=False)

        return result.json()

    def addMovieToUserHistory(self, data):
        requests.post(LEARNING_AGENT_HIST_URL, json=data, auth=(
            "movierecommender", "vast_seas_of_infinity"), verify=False)
