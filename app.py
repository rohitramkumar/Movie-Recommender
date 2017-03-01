from flask import Flask, url_for, make_response, send_file, request, jsonify, render_template
from flask_bootstrap import Bootstrap
from utils import MovieDBApiClient

app = Flask(__name__)
Bootstrap(app)

@app.route("/")
def index():
  # return make_response(open('templates/index.html').read())
  return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
  req = request.get_json(force=True)
  action = req.get('result').get('action')
  if action == "movie.filtering":
    res = processFilteringRequest(req)
  elif action == "movie.similar":
    res = processSimilarityRequest()
  r = make_response(json.dumps(res))
  r.headers['Content-Type'] = 'application/json'
  return r

def processFilteringRequest(req):
    # Init client which helps process information from themoviedb.
    client = MovieDBApiClient()
    finalDiscoveryURL = MovieDBApiClient.MOVIE_DISCOVERY_URL
    # Get all filters specified by user on api.ai.
    userSpecifiedGenres = req.get('result').get('contexts')[0].get('parameters').get('genre')
    userSpecifiedCastFirstName = req.get('result').get('contexts')[0].get('parameters').get('cast-first-name')
    userSpecifiedCastLastName = req.get('result').get('contexts')[0].get('parameters').get('cast-last-name')
    # Chat agent only allows us to parse out first and last names seperately
    # so we need to merge these to get a list of full names.
    userSpecifiedCast = [s1 + " " + s2 for s1, s2 in zip(userSpecifiedCastFirstName, userSpecifiedCastLastName)]
    userSpecifiedRating = req.get('result').get('contexts')[0].get('parameters').get('rating')
    # Get corresponding information from themoviedb.
    genreIds = client.getGenresIds(userSpecifiedGenres)
    castIds = client.getCastIds(userSpecifiedCast)
    # Construct movie discovery URL.
    finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('with_genres', genreIds))
    finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('with_people', castIds))
    finalDiscoveryURL = finalDiscoveryURL + client.encodeURLKeyValue(('certification', userSpecifiedRating))
    movies = client.getDiscoveredMovies(finalDiscoveryURL)
    if len(movies) > 0:
        speech = "I recommend the following movies: " + ', '.join(movies)
    else:
        speech = "Sorry there are no movies that match your request"
    return {
        "speech":speech,
        "displayText":speech,
        "source":"movie-recommendation-service"
    }

def processSimilarityRequest(req):
  # Init client which helps process information from themoviedb.
  client = MovieDBApiClient()
  pass

if __name__ == '__main__':
  app.run(debug=True, port='8888', host='0.0.0.0')
