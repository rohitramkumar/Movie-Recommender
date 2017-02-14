from flask import Flask, url_for, make_response, send_file, request
import os
import requests
import json
import datetime

app = Flask(__name__)


@app.route("/")
def index():
    return make_response(open('templates/index.html').read())

if __name__ == '__main__':
    app.run(debug=False, port='8888', host='0.0.0.0')
