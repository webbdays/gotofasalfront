from flask import Flask, render_template
from flask import request
import requests
import json
import os

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    # some default movies
    defaultMovies = ["RRR", "Sarkaru Vaari Paata", "Bheemla Nayak", "Sita Ramam", "Radhe Shyam", "Acharya", "Major", "F3"]

    movies = []
    for movie in defaultMovies:
        try:
            res = requests.request("GET", url=os.getenv("OMDB_URL") + "?&apikey=" + os.getenv("OMDB_API_KEY") + "&t=" + movie )
            #print(resp.json())
            #movies.append(res.json())
            #print(movies)
        except:
            print("error")
        
    return render_template("index.html", movies=movies)


@app.route("/search",methods=["POST"])
def performSearch():
    print(request.form.get("searchQuery"))
    movies = []
    try:
        res = requests.request("GET", url=os.getenv("OMDB_URL")+ "?&apikey=" + os.getenv("OMDB_API_KEY") + "&s=" + request.form.get("searchQuery"))
        #movies = res.json()["search"] # list movies details
    except:
        print("error")
    return render_template("index.html", movies=movies)

