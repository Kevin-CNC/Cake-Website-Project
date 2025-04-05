"""
By Kevin Caplescu, using the official Supabase Python repo on github:

Create client connection to supabase database and returns to main script.
"""
import supabase
import json
import random
import datetime
import os
import dotenv

from utils import encryption as encr_module
from utils import email_manager

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_info = {
    "database_url": os.getenv("SUPABASE_URL"),
    "database_key": os.getenv("SUPABASE_KEY"),
}
############################
# module helper functions #
def _generate_unique_id_():
    id = ""
    for i in range(12):
        id += str(random.randint(0,9))
        
    return id


########################################################
# Function to create a client connection to the database
def run():
    database:Client = create_client(supabase_info["database_url"], supabase_info["database_key"])
    print("Success!")
    return database

# Function to check if an email is already in use
def check_email_exists(database:Client,mail):
    try:
        if mail == None:
            return None
        
        # Command to fetch data from userbase which has the present email address
        result = database.from_("userbase").select("*").eq("email", mail).execute()
        if result.data == []:
            return(False)
        else:
            return(True)
    
    except Exception as e:
        return None


# Function to try and log in user; returns a dictionary with user's unique ID and attempt status
def login_user(database:Client,mail:str,password:str):
    status_return = {
        "attempt valid":False, # Set to 'False' by default
        "unique user id":None,
    }   
    try:
        user_data = database.from_("userbase").select("*").eq("email", encr_module.encrypt(mail)).execute()
        if user_data.data == []:
            raise ValueError("No user with that email address")
        
        user_data = user_data.data[0] # Index the actual data from the response
        
        if encr_module.decrypt(user_data["password"]) == password:
            status_return["attempt valid"] = True
            status_return["unique user id"] = encr_module.decrypt(user_data["unique_id"])

        return ( status_return )
    except Exception as e: # Fail login attempt by default
        print(e)
        return ( status_return )
        

# Function to add a new user to the database
def add_new_user(database:Client,mail:str,password:str,username:str):
    try:
        if database == None:
            return("Error with database connection, please try again later...")
        
        for argument in [mail,password,username]: # Sanitification of user-inputs
            if argument == None:
                raise ValueError("Missing arguments")
        
        chosen_id = _generate_unique_id_()
        
        empty_user_table = {
            "email":str(encr_module.encrypt(mail)),
            "password":str(encr_module.encrypt(password)),
            "unique_id":str(encr_module.encrypt(chosen_id)),
            "username":str(encr_module.encrypt(username)),
            "date_joined":str(datetime.datetime.now()),
            "confirmed_orders":[]
        }
        
        for key in empty_user_table:
            if empty_user_table[key] is None:
                raise Exception("Error with data encryption.")
        
        print("id: ",chosen_id)
        database.from_("userbase").insert([empty_user_table]).execute()
        return chosen_id
        
    except Exception as e: # Catch any errors and avoid crashing the server
        print(e)
        return None
    
    
def initialise_password_reset(database:Client,targetMail:str,emailManager:email_manager):
    generated_token = _generate_unique_id_()
    
    data = {
        "token_id": str(encr_module(_generate_unique_id_())),
        "created_at":str(datetime.datetime.now()),
        "target_mail":str(encr_module.encrypt(targetMail))
    }
    
    database.from_("reset_token").insert([data]).execute()
    email_manager.send_email(targetMail,"PASSWORD RESET!",f"""
                             You've requested a password reset for the account with email: {targetMail}.
                             You have 10 minutes to reset the password before the link below expires.
                             Link to reset password: "http://127.0.0.1:5000/reset_password_setup/?request-token:{generated_token}"
                             
                             If this was NOT you, please ignore this email.
                             """)
    
    