from flask import Flask

# WSGI callable
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
  req = request.get_json(silent=True, force=True)
  speech = "We recommend you to watch the Fugitive."
  return {
    "speech": speech,
    "displayText": speech,
    "source": "apiai-weather-webhook-sample"
  }
