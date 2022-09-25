from flask import Flask, render_template, redirect 
from flask import request
from pymongo import MongoClient
import requests
import json
import os
import bcrypt
import jwt
import datetime
import asyncio


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
    moviesdata = []
    # for movie in defaultMovies:
    #     try:
    #         url = os.getenv("OMDB_URL") + "?&apikey=" + os.getenv("OMDB_API_KEY") + "&t=" + movie
    #         res = requests.request("GET", url=url )
    #         moviesdata.append(res.json())
    #     except:
    #         print("error")
    moviesdata = async_get_movies_data(defaultMovies)
    return render_template("home.html", user_email=dtoken["email"], movies=moviesdata)

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
    
    
    userdata["password"]= hashedPassword
    insertOneResult1 = userCollection.insert_one(userdata)
    insertOneResult2 = userfavmoviesCollection.insert_one({"user_email":userdata["email"],"fav_movies_lists":[]})
    
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
    
    searchmovies = []
    try:
        url = os.getenv("OMDB_URL")+ "?&apikey=" + os.getenv("OMDB_API_KEY") + "&s=" + request.form.get("searchQuery")
        res = requests.request("GET", url=url)
        searchmovies = [ movie["Title"] for movie in res.json()["Search"] ] # list of movies details
    except:
        print("error")

    moviesdata = async_get_movies_data(searchmovies)

    return render_template("home.html", movies=moviesdata)

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

    listdetails = {}
    listsaccess = {}
    
    fav_movies_list_cursor = userfavmoviesCollection.find({"user_email":user_email})
    if not fav_movies_list_cursor :
        return render_template("user_profile.html", user_name=user_name, listdetails=listdetails, listsaccess=listsaccess)
        
    
    for list in fav_movies_list_cursor:
        user_fav_movies_names = list["fav_movies"]
        if user_fav_movies_names :
            # for movie in user_fav_movies_names:
            #     try:
            #         url = os.getenv("OMDB_URL") + "?&apikey=" + os.getenv("OMDB_API_KEY") + "&t=" + movie
            #         res = requests.request("GET", url=url )
            #         user_fav_movies_details.append(res.json())
            #     except:
            #         print("error")
            listdetails[list["fav_movies_list_name"]] = async_get_movies_data(user_fav_movies_names)
            listsaccess[list["fav_movies_list_name"]] = list["access"]
    print(listdetails)
        
    return render_template("user_profile.html", user_name=user_name, listdetails=listdetails, listsaccess=listsaccess)

@app.route("/user_profile/<other_user_email>", methods=["GET"])
def other_user_profile(other_user_email):

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

    fav_movies_list_cursor = userfavmoviesCollection.find({"user_email":other_user_email, "access": "public"})
        
    listdetails = {}
    listsaccess = {}
    for list in fav_movies_list_cursor:
        user_fav_movies_names = list["fav_movies"]
        if user_fav_movies_names :
            # for movie in user_fav_movies_names:
            #     try:
            #         url = os.getenv("OMDB_URL") + "?&apikey=" + os.getenv("OMDB_API_KEY") + "&t=" + movie
            #         res = requests.request("GET", url=url )
            #         user_fav_movies_details.append(res.json())
            #     except:
            #         print("error")
            listdetails[list["fav_movies_list_name"]] = async_get_movies_data(user_fav_movies_names)
            listsaccess[list["fav_movies_list_name"]] = list["access"]
    print(listdetails)
        
    return render_template("other_user_profile.html", listdetails=listdetails, listsaccess=listsaccess, other_user_email=other_user_email)



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

    data = dict(request.get_json())
    print(data)
    fav_movies = []
    fav_movies.append(data["movie_name"])
    print(fav_movies)
    favmovie_list_name = data["favmovie_list_name"]

    if data["action"] == "add":
        # userfavmovies = userfavmoviesCollection.insert_one({"user_email":dtoken["email"], "fav_movies_list_name":favmovie_list_name, "access":"private", "fav_movies":[]})
        userfavmovies = userfavmoviesCollection.find_one_and_update({"user_email":dtoken["email"], "fav_movies_list_name":favmovie_list_name}, { "$addToSet" : { "fav_movies": {"$each": fav_movies}} })
        if not userfavmovies :
            userfavmovies = userfavmoviesCollection.insert_one({"user_email":dtoken["email"], "fav_movies_list_name":favmovie_list_name, "access":"private", "fav_movies":fav_movies})
    elif data["action"] == "remove":
        userfavmovies = userfavmoviesCollection.update_one({"user_email":dtoken["email"], "fav_movies_list_name":favmovie_list_name}, {"$pull" : { "fav_movies": {"$in": fav_movies}} })
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
    
    # save in db that user email is verified
    updateResult = userCollection.update_one({"email":email_verify_form["email"]}, {"$set":{"email_verify":True}})

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



@app.route("/favmovieslistaccess", methods=["POST"])
def favmovieslistaccess():

    token = request.cookies.get("token")
    # verify the jwt token
    try:
        dtoken = jwt.decode(token,os.getenv("JWT_MAIN_SECRET"), algorithms=["HS256"])
    except : # jwt.ExpiredSignatureError:
        return redirect("/signin_page")
    
    data = dict(request.get_json())
    favmovie_list_name = data["favmovie_list_name"]
    userfavmovies = userfavmoviesCollection.find_one_and_update({"user_email":dtoken["email"], "fav_movies_list_name":favmovie_list_name}, { "$set" : { "access": data["access"]} })
    if userfavmovies:
        return {"status":f"List: {favmovie_list_name} is made {data['access']}"}




# get movies in async manner.
def async_get_movies_data(searchmovies):
        urlprefix = os.getenv("OMDB_URL") + "?&apikey=" + os.getenv("OMDB_API_KEY") + "&t=" 
        
        async def getmovie(movie):
            try:
                url =  urlprefix + movie
                res = requests.request("GET", url=url )
            except:
                print("error")
            
            return res.json()
        
        async def getmoviesdata():
            # return
            return await asyncio.gather(*[getmovie(movie) for movie in searchmovies])
        
        return asyncio.run(getmoviesdata())



