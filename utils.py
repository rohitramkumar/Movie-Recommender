import requests
import json
import urllib
import os

BING_SC_API_KEY = os.environ['BING_SC_API_KEY']
MOVIE_DB_API_KEY = os.environ['MOVIE_DB_API_KEY']
# Database that provides simple filtering.
MOVIE_DB_URL = 'https://api.themoviedb.org/3/'
# URL Endpoints for different types of filtering data.
GENRES_URL = (MOVIE_DB_URL + 'genre/movie/list?api_key={}&language=en-US').format(MOVIE_DB_API_KEY)
PEOPLE_SEARCH_URL = (MOVIE_DB_URL + 'search/person?api_key={}&language=en-US&query={}&page=1&include_adult=false')
MOVIE_SEARCH_URL = (MOVIE_DB_URL + 'search/movie?api_key={}&language=en-US&query={}&page=1&include_adult=false')
# URL Endpoint for movie discovery
MOVIE_DISCOVERY_URL = (MOVIE_DB_URL + 'discover/movie?api_key={}&include_adult=false&include_video=false&language=en-US&sort_by=popularity.desc').format(MOVIE_DB_API_KEY)
# URL Endpoint for movie similarity
MOVIE_SIMILARITY_URL = (MOVIE_DB_URL + 'movie/{}/similar?api_key={}&language=en-US')
# URL Endpoint for spell checking
BING_SC_URL = 'https://api.cognitive.microsoft.com/bing/v5.0/spellcheck/?mode=proof&mkt=en-us'
# TODO: maybe make this user configurable
MAX_RESULTS = 5


def spellCheck(query):
  """Given a potentially misspelled query, return the correct spelling with
  the proper punctuation, capitalization, etc if necessary. Uses the Bing
  Spell Check API."""

  newQuery = query
  encodedQuery = urllib.quote_plus(query)
  url = BING_SC_URL + '&text=' + encodedQuery
  headers = {'Content-Type': 'application/x-www-form-urlencoded','Ocp-Apim-Subscription-Key': '1c964897dce84d8cb04b5e8ff4634d48'}
  spellCheckResponse = requests.post(url, headers=headers)
  spellCheckInfo = json.loads(spellCheckResponse.text)
  for flaggedToken in spellCheckInfo.get('flaggedTokens'):
    token = flaggedToken.get('token')
    suggestion = flaggedToken.get('suggestions')[0].get('suggestion')
    newQuery = newQuery.replace(token, suggestion)
  return newQuery

class MovieDBApiClient:
  """This class abstracts API calls for the api.themoviedb.org."""

  def __init__(self):
    pass

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
      castRequestResult = requests.get(PEOPLE_SEARCH_URL.format(MOVIE_DB_API_KEY, urllib.quote_plus(cast)))
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
    while counter < MAX_RESULTS and counter < len(movieInfo.get('results')):
      movies.append(movieInfo.get('results')[counter].get('title'))
      counter += 1
    return movies

  def getSimilarMovies(self, benchmarkMovie):
    """Given a benchmark movie, return a list of movies that are similar."""

    similarMovies = []
    # First, get the id of the movie given the name.
    benchmarkMovieIdResult = requests.get(MOVIE_SEARCH_URL.format(MOVIE_DB_API_KEY, urllib.quote_plus(benchmarkMovie)))
    benchmarkMovieIdInfo = json.loads(benchmarkMovieIdResult.text)
    if len(benchmarkMovieIdInfo.get('results')) > 0:
      benchmarkMovieId = benchmarkMovieIdInfo.get('results')[0].get('id')
      # Get the similar movies given the movie id.
      movieSimilarityResult = requests.get(MOVIE_SIMILARITY_URL.format(benchmarkMovieId, MOVIE_DB_API_KEY))
      movieSimilarityInfo = json.loads(movieSimilarityResult.text)
      counter = 0
      while counter < MAX_RESULTS and counter < len(movieSimilarityInfo.get('results')):
        similarMovies.append(movieSimilarityInfo.get('results')[counter].get('title'))
        counter += 1
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

  def __init__(self, user):
    self.user = user

  def getRecommendedMovies(self):
    pass
