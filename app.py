import logging
import os
import socket
import http.client
import json, requests
from unittest import expectedFailure
from datetime import timedelta
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from waitress import serve

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
print('BASE_DIR', BASE_DIR)

app = Flask(__name__)

logging.basicConfig(filename='flask-tailwind.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app.config['SECRET_KEY'] = 'BDy9asydnasdna98n^B&D*tsa87dvbats67asrv67r'

### Uncomment this to use Database Server 
# POSTGRES = {
#     'user': 'uer',
#     'pw': 'password',
#     'db': 'db_name',
#     'host': 'db_host',
#     'port': 'db_port',
# }
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask-tailwind.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

def getplayingData():
    try:
        resp = requests.get("https://localhost:5000/api/getplaying")
        text = resp.text
        data = json.loads(text)
        if data['success'] == 'true':
            return data
        elif data['success'] == 'false':
            data['image'] = './static/img/song.webp'
        else:
            return data
    except:
        data={"StatusCode": None, "artist": None, "image": "./static/img/song.webp", "mbid": None, "nowplaying": False, "songtitle": None, "success": False}
        return data

def lastfm_get():
    # define headers and URL
    url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=lukxee&api_key=4982e09a2804137c53cda2fbbde4d046&format=json&limit=1'

    response = requests.get(url)
    return response

def getartistdata():
    try: 
        resp = requests.get("https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user=lukxee&api_key=4982e09a2804137c53cda2fbbde4d046&format=json&limit=10")
        text = resp.text
        data = resp.json()
        return data
    except:
        data = None
        return data

# def getplexstatus():
#     conn = http.client.HTTPConnection("plex.lukxee.com", timeout=0.25)
#     conn.request("HEAD", "/")
#     try:
#         r1 = conn.getresponse()
#         status_code = str(r1.status)
#     except http.client.HTTPException:
#         print("Request error")
#         return "400"
#     except TimeoutError:
#         print("Timeout error")
#         return "400"
#     except socket.timeout as st:
#         print("Timeout error")
#         return "400"
#     else:
#         #print(status_code)
#         return status_code
#     finally:
#         conn.close()

@app.route('/api/getplaying', methods=["GET", "POST"])
def data():
    try:
        response = lastfm_get()
        songtitle = response.json()['recenttracks']['track'][0]['name']
        artist = response.json()['recenttracks']['track'][0]['artist']['#text']
        image = response.json()['recenttracks']['track'][0]['image'][2]['#text']
        mbid = response.json()['recenttracks']['track'][0]['mbid']
        nowplaying = response.json()['recenttracks']['track'][0]['@attr']['nowplaying']
        return jsonify({"success": True, "StatusCode": response.status_code, "songtitle": songtitle, "artist": artist, "image": image, "mbid": mbid, "nowplaying": nowplaying}) #jsonify({"success": True})
    except:
        return jsonify({"success": False, "StatusCode": None, "songtitle": None, "artist": None, "image": None, "mbid": None, "nowplaying": False})

@app.route("/")
def root():
    return render_template('index.html', Name="Home", data=getplayingData())

@app.route('/widget')
def widget():
    return render_template('widget.html', Name="Widget", data=getplayingData())

@app.route('/clock')
def clock():
    return render_template('clock.html', Name="Clock", data=None)

@app.route('/movies&tv')
def movie_tv():
    return render_template('movies-tv.html', Name="Movies & TV", data=None)

@app.route('/artists')
def artists():
    return render_template('artists.html', Name="Top Artists", data=getartistdata())

@app.route('/projects')
def projects():
    return render_template('projects.html', Name="Projects", data=None)

@app.route('/reading')
def reading():
    return render_template('reading.html', Name="Reading", data=None)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', Name="Page not found", data=None)

if __name__ == '__main__':  # Declare the main application
    serve(app, host='0.0.0.0', port=1300)
    #app.run(host='0.0.0.0', debug=True, port=50500)
