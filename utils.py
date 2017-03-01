import requests
import json
import urllib
import os

API_KEY = os.environ['MOVIE_DB_API_KEY']
# Database that provides simple filtering.
MOVIE_DB_URL = 'https://api.themoviedb.org/3/'
# URL Endpoints for different types of filtering data.
GENRES_URL = (MOVIE_DB_URL + 'genre/movie/list?api_key={}&language=en-US').format(API_KEY)
PEOPLE_SEARCH_URL = (MOVIE_DB_URL + 'search/person/?api_key={}&language=en-US&query={}&page1&include_adult=false')
# URL Endpoint for movie discovery
MOVIE_DISCOVERY_URL = (MOVIE_DB_URL + 'discover/movie?api_key={}&include_adult=false&include_video=false&language=en-US&sort_by=popularity.desc').format(API_KEY)
# URL Endpoint for movie similarity
MOVIE_SIMILARITY_URL = (MOVIE_DB_URL + 'movie/{}/similar?api_key={}&language=en-US'
# TODO: maybe make this user configurable
MAX_RESULTS = 5

class MovieDBApiClient:

  def __init__(self):
      pass

  def getGenresIds(self, userSpecifiedGenres):
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
    castIds = []
    for cast in userSpecifiedCast:
      castRequestResult = requests.get(PEOPLE_SEARCH_URL.format(API_KEY, urllib.quote_plus(cast)))
      castInfo = json.loads(castRequestResult.text)
      if len(castInfo.get('results')) > 0:
        castIds.append(castInfo.get('results')[0].get('id'))
    return castIds

  def getDiscoveredMovies(self, discoveryURL):
    movieDiscoveryRequest = requests.get(discoveryURL)
    movieDiscoveryResults = json.loads(movieDiscoveryRequest.text)
    movies = []
    counter = 0
    while counter < MAX_RESULTS and counter < len(movieDiscoveryResults.get('results')):
      movies.append(movieDiscoveryResults.get('results')[counter].get('title'))
      counter += 1
    return movies

  def getSimilarMovies(self, benchmarkMovie):
    movieSimilarityRequest = requests.get(MOVIE_SIMILARITY_URL.format(urllib.quote_plus(benchmarkMovie), API_KEY))
    movieSimilarityResults = json.loads(movieSimilarityRequest.text)
    similarMovies = []
    counter = 0
    while counter < MAX_RESULTS and counter < len(movieSimilarityResults.get('results')):
      similarMovies.append(movieSimilarityResults.get('results')[counter].get('title'))
      counter += 1
    return similarMovies

  def encodeURLKeyValue(self, pair):
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

    def __init__(self, user):
        self.user = user

    def getRecommendedMovies(self):
        pass
