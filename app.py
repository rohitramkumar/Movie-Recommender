from flask import Flask, url_for, make_response, send_file, request, jsonify
import os
import requests
import json
import datetime
import urllib

app = Flask(__name__)

# Database that provides simple filtering.
MOVIE_DB_URL = 'https://api.themoviedb.org/3/'
API_KEY = os.environ['MOVIE_DB_API_KEY']

# URL Endpoints for different types of filtering data.
GENRES_URL = (MOVIE_DB_URL + 'genre/movie/list?api_key={}&language=en-US').format(API_KEY)
PEOPLE_SEARCH_URL = (MOVIE_DB_URL + 'search/person/?api_key={}&language=en-US&query={}&page1&include_adult=false')

# URL Endpoint for movie discovery
MOVIE_DISCOVERY_URL = (MOVIE_DB_URL + 'discover/movie?api_key={}&include_adult=false&include_video=false&language=en-US&sort_by=release_date.desc').format(API_KEY)

MAX_RESULTS = 5

@app.route("/")
def index():
    return make_response(open('templates/index.html').read())

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    res = processRequest(req)
    r = make_response(json.dumps(res))
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    # The final URL which will allow us to retrieve recommendations based on filters. Initially it is just the base url.
    finalDiscoveryURL = MOVIE_DISCOVERY_URL
    userSpecifiedGenres = req.get('result').get('contexts')[0].get('parameters').get('genre')
    # If the user did not specify genre to chat agent, then do not bother get the genre id's.
    if len(userSpecifiedGenres) != 0:
        genreRequestResult = requests.get(GENRES_URL)
        genres = json.loads(genreRequestResult.text)
        # For each user specified genre, find its corresponding genre id
        genreIds = []
        for userSpecifiedGenre in userSpecifiedGenres:
            for genre in genres['genres']:
                if userSpecifiedGenre == genre['name']:
                    genreIds.append(genre['id'])
        finalDiscoveryURL = finalDiscoveryURL + '&with_genres=' + ''.join(str(g) for g in genreIds)
    userSpecifiedCast = req.get('result').get('contexts')[0].get('parameters').get('cast')
    # If the user did not specify cast to the chat agent, then do not bother getting cast id's.
    if len(userSpecifiedCast) != 0:
        castIds = []
        for cast in userSpecifiedCast:
            castRequestResult = requests.get(PEOPLE_SEARCH_URL.format(API_KEY,urllib.quote_plus(cast)))
            castInfo = json.loads(castRequestResult.text)
            if len(castInfo.get('results')) > 0:
                castIds.append(castInfo.get('results')[0].get('id'))
        finalDiscoveryURL = finalDiscoveryURL + '&with_people=' + ''.join(str(c) for c in castIds)
    userSpecifiedRating = req.get('result').get('contexts')[0].get('parameters').get('rating')
    # If the user did not specify an mpaa rating, then do not bother putting it in the final url string
    if userSpecifiedRating != '':
        finalDiscoveryURL = finalDiscoveryURL + '&certification=' + userSpecifiedRating
    # Construct final URL.
    movieDiscoveryRequest = requests.get(finalDiscoveryURL)
    movieDiscoveryResults = json.loads(movieDiscoveryRequest.text)
    recommendations = []
    if len(movieDiscoveryResults.get('results')) > 0:
        counter = 0
        while counter < MAX_RESULTS:
            recommendations.append(movieDiscoveryResults.get('results')[counter].get('title'))
    if len(recommendations) > 0:
        speech = "I recommend the following movies: " + ''.join(recommendations)
    else:
        speech = "Sorry there are no movies that match your request"
    return 
    {
        "speech":speech,
        "displayText":speech,
        "source":"movie-recommendation-service"

    }
    
if __name__ == '__main__':
    app.run(debug=False, port='8888', host='0.0.0.0')
