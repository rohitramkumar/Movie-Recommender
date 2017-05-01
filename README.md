# Movie Recommendation Service
<a href="https://movie-recommendation-service.herokuapp.com/"> Link </a>

Movie recommender is a project that recommends movies through an intelligent chat agent that a user can interact with. User's can ask for personalized movie suggestions if they register for a user account and build a movie watch-list. 

This repo contains the front-end, api.ai, and database model components of the movie recommender project. The learning portion of the project can be found <a href="https://github.com/Slash0BZ/movie_recommender">here.</a>

# Overall architecture

![alt text](http://imgur.com/YfZeexN.png)

# Code and File Structure

app.py - Contains the main flask route which is hit by the api.ai chat agent.

app_utils.py - Contains utility classes (MovieABApiClient) and functions used in app.py webapi.py - Contains API which is used by the front-end 

static/js/app.js - Contains all Angular.JS states and controllers which control each aspect of the web application.  

static/js/services.js - Contains the primary user service which handles all HTTP request with the backend flask API (webapi.py). The Flask API in turn helps communicate with the chat agent, learning server or database. 

static/partials - Contains all HTML files which are used by each Angular.JS state. For example, we have separate html files for the login page, movie-detail partial and view-profile page. 

webapi_utils.py - Contains utility functions to communicate with the underlying postgresql database. Also includes the learning agent classes.

model.py - Contains database model information for user database.

templates/app.spec.html - Tests for the front-end using jasmine.js framework.

tests.py - Contains unit tests for the chat agent functionality as well as back-end API calls.

# Detailed Documentation

Click <a href="https://docs.google.com/document/d/1zR0i8IYlvWiY05bJxtEwA6mh7qu2QsVhHCduVYH3JLA/edit?usp=sharing"> here</a>.

# Install and Deploy

The flask server is in app.py on the repo root. 

The web-site can be deployed on Heroku by simply configuring the dashboard to pull from this git repo. 

Any and all requirements are in requirements.txt, all dependencies are automatically installed by Heroku.

# Packaging

The main Flask server is packaged in app.py and does not require any special instructions for deployment on Heroku.

# Contributors List

ramkumr2, hskhan10, amthoma3, ziweiba2, zwen6
