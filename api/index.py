from flask import Flask, render_template, redirect 
from flask import request
from pymongo import MongoClient
import requests
import json
import os
import bcrypt
import jwt
import datetime


# import custom modules
from .emailHandler import *

# flask app
app = Flask(__name__)


# connect to mongodb with the mongodb client
mongoDBClient = MongoClient("mongodb+srv://Cluster0:" + os.getenv("MONGODB_PASSWORD") + "@cluster0.gxamoya.mongodb.net/?retryWrites=true&w=majority")
gotofasalDB = mongoDBClient["gotofasal"]
userCollection = gotofasalDB.user
userfavmoviesCollection = gotofasalDB.userfavmovies


@app.route("/", methods=["GET"])
def index():

    # autenticate user with the help of jwt
    token = request.cookies.get("token")

    # verify the jwt token
    try:
        jwt.decode(token,os.getenv("JWT_MAIN_SECRET"), algorithms=["HS256"])
        return redirect("/home")
    except:
        print("err")
    
    return render_template("index.html")

@app.route("/home", methods=["GET"])
def home():
    # autenticate user with the help of jwt
    token = request.cookies.get("token")

    # verify the jwt token
    try:
        dtoken = jwt.decode(token,os.getenv("JWT_MAIN_SECRET"), algorithms=["HS256"])
    except:
        return redirect("/signin_page")
    
    # some default movies
    defaultMovies = ["RRR", "Sarkaru Vaari Paata", "Bheemla Nayak", "Sita Ramam", "Radhe Shyam", "Acharya", "Major", "F3"]
    movies = []
    for movie in defaultMovies:
        try:
            url = os.getenv("OMDB_URL") + "?&apikey=" + os.getenv("OMDB_API_KEY") + "&t=" + movie
            res = requests.request("GET", url=url )
            movies.append(res.json())
        except:
            print("error")
    return render_template("home.html", user_email=dtoken["email"], movies=movies)

@app.route("/signup_page", methods=["GET"])
def signup_page():
    return render_template("signup.html")

@app.route("/signin_page", methods=["GET"])
def signin_page():
    return render_template("signin.html")

@app.route("/signup", methods=["POST"])
def signup():
    # get the submitted user registeration form from the body in the request
    registrationForm = dict(request.form)

    # check if user already registered.
    check = userCollection.find_one({'email':registrationForm["email"]})
    if check :
        return render_template("alreadyRegistered.html")
    

    userdata = dict(registrationForm)
    userdata["email_verify"] = False

    # hash the password and save the user details in db(mongodb).
    hashedPassword = bcrypt.hashpw(registrationForm["password"].encode("utf-8"), bcrypt.gensalt())
    registrationForm["password"] = hashedPassword
    insertOneResult1 = userCollection.insert_one(userdata)
    insertOneResult2 = userfavmoviesCollection.insert_one({"user_email":userdata["email"],"fav_movies":[]})
    
    verify_user_email_token_generator(registrationForm["email"])

    # redirect the user to signin page.
    return redirect("/signin_page")

@app.route("/signin", methods=["POST"])
def signin():

    # autenticate user with the help of jwt
    token = request.cookies.get("token")
    try:
        jwt.decode(token,os.getenv("JWT_MAIN_SECRET"), algorithms=["HS256"])
        return redirect("/home")
    except:
        print("err")

    # get the submited form from body in the request
    singinForm = dict(request.form)

    # check if user already exist.
    user = userCollection.find_one({"email":singinForm["email"]})
    if not user :
        return render_template("userNotRegistered.html")
    
    # check if user email is verified
    if not user["email_verify"] :
        return redirect("/email_verify_page")
    
    # Authenicate user password witht the hash in the db
    if not bcrypt.checkpw(singinForm["password"].encode("utf-8"), user["password"]):
        return {"status": "Wrong password, try again"}
    
    # Generate jwt token for the subsequent authentication for other routes.
    # need to invalidate token after about 20-30min, user need to re-login
    token = jwt.encode({"name":user["name"], "email":user["email"], "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, os.getenv("JWT_MAIN_SECRET"))

    
    # redirect user to home page
    response = redirect("/home" )
    response.set_cookie(key="token", value=token, httponly=True)
    return response

@app.route("/search",methods=["POST"])
def performSearch():

    token = request.cookies.get("token")

    # verify the jwt token
    try:
        jwt.decode(token,os.getenv("JWT_MAIN_SECRET"), algorithms=["HS256"])
    except : #jwt.ExpiredSignatureError:
        return redirect("/signin_page")
    # except:
    #     return {"status":"provide proper jwt token or login again"}
    
    movies = []
    try:
        url = os.getenv("OMDB_URL")+ "?&apikey=" + os.getenv("OMDB_API_KEY") + "&s=" + request.form.get("searchQuery")
        res = requests.request("GET", url=url)
        movies = res.json()["Search"] # list of movies details
    except:
        print("error")
    print(movies)
    return render_template("home.html", movies=movies)

@app.route("/user_profile", methods=["GET"])
def user_profile():

    token = request.cookies.get("token")

    # verify the jwt token
    try:
        dtoken = jwt.decode(token ,os.getenv("JWT_MAIN_SECRET"), algorithms=["HS256"])
    except : # jwt.ExpiredSignatureError:
        return redirect("/signin_page")
    # except:
    #     return {"status":"provide proper jwt token or login again"}
    
    user_email = dtoken["email"]
    user_name = dtoken["name"]

    user_fav_movies_names = userfavmoviesCollection.find_one({"user_email":user_email})["fav_movies"]

    user_fav_movies_details = []
    if user_fav_movies_names :
        for movie in user_fav_movies_names:
            try:
                url = os.getenv("OMDB_URL") + "?&apikey=" + os.getenv("OMDB_API_KEY") + "&t=" + movie
                res = requests.request("GET", url=url )
                user_fav_movies_details.append(res.json())
            except:
                print("error")
    
    return render_template("user_profile.html", user_name=user_name, user_fav_movies=user_fav_movies_details)

@app.route("/favmovie", methods=["POST"])
def favmovies():
    token = request.cookies.get("token")
    # verify the jwt token
    try:
        dtoken = jwt.decode(token,os.getenv("JWT_MAIN_SECRET"), algorithms=["HS256"])
    except : # jwt.ExpiredSignatureError:
        return redirect("/signin_page")
    # except:
    #     return {"status":"provide proper jwt token or login again"}
    
    user_name = dtoken["name"]

    fav_movies = []
    data = dict(request.get_json())
    
    fav_movies.append(data["movie_name"])
    if data["action"] == "add":
        userfavmovies = userfavmoviesCollection.update_one({"user_email":dtoken["email"]}, {"$addToSet": {"fav_movies": {"$each": fav_movies}}}) 
    elif data["action"] == "remove":
        userfavmovies = userfavmoviesCollection.update_one({"user_email":dtoken["email"]}, {"$pull": {"fav_movies": {"$in": fav_movies}}})
    else:
        return {"status": "no action taken. Invalid input" }
    return {"status": "action : "+ data["action"] + "permformed on user fav movies"}


@app.route("/signout", methods=["GET"])
def signout():

    token = request.cookies.get("token")
    try:
        dtoken = jwt.decode(token,os.getenv("JWT_MAIN_SECRET"), algorithms=["HS256"])
        dtoken["exp"] = 0
        token = jwt.encode(dtoken, os.getenv("JWT_MAIN_SECRET"))

        # redirect user to home page
        response = redirect("/home" )
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    except:
        return redirect("/signin")
        
    return redirect("/")



@app.route("/email_verify_page", methods=["GET"])
def email_verify_page():
    return render_template("email_verify_page.html")

@app.route("/email_verify", methods=["POST"])
def email_verify():
    email_verify_form = dict(request.form)
    email_verify_token = email_verify_form["email_verify_token"]
    try:
        jwt.decode(email_verify_token, os.getenv("EMAIL_VERIFY_MAIN_SECRET"), algorithms=["HS256"])
    except:
        return redirect("/email_verify_page")
    return redirect("/home")

@app.route("/generate_email_verify_token", methods=["POST"])
def generate_email_verify_token():
    data = dict(request.form)

    # check if user already exist.
    user = userCollection.find_one({"email":data["email"]})
    if not user :
        return render_template("userNotRegistered.html")

    verify_user_email_token_generator(data["email"])
    return redirect("/email_verify_page")