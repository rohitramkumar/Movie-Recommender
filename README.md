# Movie Recommendation Service

This repo contains the front-end and api.ai components of the movie recommender project. The learning portion of the project can be found <a href="https://github.com/Slash0BZ/movie_recommender">here.</a>

Movie recommender is a project that recommends movies based on two factors: the trending/in-theater movies and the recommendation based on a user's watched movie histories. 
We provide an API for the front end to use the recommendation services.

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

# Install and Deploy

The flask server is in app.py on the repo root. 

The web-site can be deployed on Heroku by simply configuring the dashboard to pull from this git repo. 

Any and all requirements are in requirements.txt, all dependencies are automatically installed by Heroku.

# Packaging

The main Flask server is packaged in app.py and does not require any special instructions for deployment on Heroku.
