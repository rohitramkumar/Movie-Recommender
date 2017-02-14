from flask import Flask, url_for, make_response, send_file, request
import os
import requests
import json

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    response = app.make_response(send_file("templates/index.html"))
    response.headers['Last-Modified'] = datetime.now()
    response.headers[
        'Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'

    return response

if __name__ == '__main__':
    app.run(debug=False, port='8888', host='0.0.0.0')
