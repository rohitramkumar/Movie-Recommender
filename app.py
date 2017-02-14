from flask import Flask, url_for, make_response, send_file, request
import os
import requests
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return send_file("templates/index.html")

if __name__ == '__main__':
    app.run(debug=False, port='8888', host='0.0.0.0')
