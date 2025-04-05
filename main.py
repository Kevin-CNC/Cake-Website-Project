# Group 12 - Cake Website
# Main backend for the website #
#  Libraries & modules imports #
import flask
import flask_limiter
import os
import threading
import dotenv
import requests
import datetime
import validate_email_address
import utils # Custom modules created by us

from utils import database as db_module
from utils import email_manager

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from threading import Thread
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from validate_email_address import validate_email

api_version = "v1"
load_dotenv()

"""" 
Holds an 'Account' object from the supabase module
Due to overhead between connections, web-app is run first while database is loading
"""
database = None
def _connect_database():
    global database
    
    if database == None:
        database = db_module.run()

# Flask app creation #
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.session_cookie_name = f"cakedUpCookie{api_version}"

# Email Manager
EMAIL_MANAGER = email_manager.EmailManager()

# Rate limiter setup #
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["99999999 per hour"])


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30) # User cache is held for up to 30 days.

@app.route("/")
def index():
    session["isAdminKey"] = None
    
    if app.debug: 
        session["userId"] = None # Debugging purposes only, remove this line in production.
        
    return render_template("index.html") # Remember in Flask you ALWAYS return something to the user, else everything crashes.

@app.route("/admin-login")
def adminlog():
    return( render_template("admin-login.html") )

@app.route("/login")
def login():
    return( render_template("login.html") )

@app.route("/signin")
def signin():
    return( render_template("sign-in.html") )

@app.route("/reset")
def recover():
    return( render_template("recovery.html") )

@app.route("/admin-panel")
def showPanel():
    try:
        if session["isAdminKey"]:
            return( render_template("adminstatus.html") )
        else:
            redirect("/")
        
    except Exception as e:
        redirect("/")

######################## API Endpoints ##################################

# this is a simple test endpoint; use it as a base to create future endpoints too!
@app.route(f"/api/{api_version}/test", methods=["GET", "POST"])
@limiter.limit("3/second") 
def test():
    try:
        if request.method == "GET":
            print("It's a GET request! Woah!")
        elif request.method == "POST":
            print("It's a POST request! Yippie!")
        else:
            print(f"It's a {request.method} request!")
        
        request_data = request.get_json() # for any json data sent to the endpoint
        # print(request_data)
        
        return jsonify("The test endpoint works fully!")
    
    except:
        return jsonify("The test endpoint failed, oh noes!")

 # Login API call
@app.route(f"/api/{api_version}/login", methods=["POST"])
@limiter.limit("1/second") # Limits the endpoint to 1 request per second
def logIn():
    try:
        request_data = request.get_json()
        sent_data = {
            "email": request_data.get("email"),
            "password": request_data.get("password")
        }
        
        login_result = db_module.login_user(database,sent_data["email"],sent_data["password"])
        
        if login_result["attempt valid"]:
            session["userId"] = login_result["unique user id"]
            
            return redirect(url_for("userboard",userid=login_result["unique user id"]))
        else:
            return jsonify("Invalid login credentials, try again!")
        
    except:
        return(jsonify("Internal error, please contact customer support for more information..."))


# password API call #
@app.route(f"/api/{api_version}/reset-password",methods=["POST"])
@limiter.limit("1/second") # Limits the endpoint to 1 request per second
def reset_password():
    try:
        request_data = request.get_json()
        sent_data = {
            "email": request_data.get("email"),
        }
        
        if db_module.check_email_exists(sent_data["email"]): # only start the process of password reset IF the email exists already.
            db_module.initialise_password_reset(database,sent_data["email"],EMAIL_MANAGER)
            
    except Exception as e:
        print(f"Exception during password reset: {e}")
        
        
@app.route(f"/api/{api_version}/admin-auth",methods=["POST"])
@limiter.limit("1/second") # Limits the endpoint to 1 request per second
def adminAuth():
    try:
        req_data = request.get_json()
        sent_data = {
            "password": req_data.get("password"),
            "username": req_data.get("username")
        }
        
        if sent_data["username"] == "admin" and sent_data["password"] == "123cake":
            session["isAdminKey"] = True
            print("redirect")
            return redirect( url_for("showPanel") )
        else:
            return flash("Invalid credentials...")
        
    except Exception as e:
        print("error: ",e)
        return()
        

@app.route(f"/api/{api_version}/sign-up", methods=["POST"])
@limiter.limit("1/second") # Limits the endpoint to 1 request per second
def signUp():
    try:
        req_data = request.get_json()
        sent_data = {
            "email": req_data.get("email"),
            "password": req_data.get("password"),
            "username": req_data.get("username")
        }
        
        """ if not(validate_email(sent_data["email"], verify = True)):
            return jsonify("Not a valid email...") """
        
        # note: all database-related functions must be in the db_module
        is_using_same_mail = db_module.check_email_exists(database,sent_data["email"])
        
        if is_using_same_mail is None:
            return jsonify("Error with database connection, please try again later...")
        elif is_using_same_mail == False:


            generated_id = db_module.add_new_user(database,sent_data["email"],sent_data["password"],sent_data["username"])
            print("Done!")                
            session["userId"] = generated_id # caches the user's id in the session
            
            try:
                EMAIL_MANAGER.send_email(sent_data["email"],"CakedUp Account Creation!","Hey There!\nThanks for signing up! You can now log into our website in the future! :)")
            except Exception as e:
                print("Error with sending email to customer.")
                print("Error: ", e)
            finally:
                if app.debug:
                    return jsonify("Success message") # DEBUG OUTPUT WHEN RUNNING THE APP ON 'debug' MODE
                else:
                    return redirect(url_for("userboard"),userid=generated_id)
                
        else:
            return jsonify("Email already in use!")
    except Exception as e:
        print("exception: ",e)

if __name__ == "__main__":
    Thread(target=_connect_database).start()
    app.run(debug=True)