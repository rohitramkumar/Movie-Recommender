from flask import Flask, make_response, request
import os
import requests
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=False, port='8888', host='0.0.0.0')
