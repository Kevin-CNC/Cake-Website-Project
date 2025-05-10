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
def check_common_email(database:Client,mail:str):
    try:
        if mail == None:
            return None
        
        # Command to fetch data from userbase which has the present email address
        result = database.from_("userbase").select("email").execute()
        if result.data == []:
            print("No email found in the database")
            return False # If no email is found, return False
        
        for record in result.data:

            retrieved_email = encr_module.decrypt(record['email']) # Decrypt and decode the email address
            # Fail the check if the same email is found or there is an error with the decryption
            if retrieved_email == mail:
                return True
        
        return False # If no email matches the one in the database, return False
    
    except Exception as e:
        print("Error: " + str(e))
        return None


# Function to try and log in user; returns a dictionary with user's unique ID and attempt status
def login_user(database:Client,mail:str,password:str):
    status_return = {
        "attempt valid":False, # Set to 'False' by default
        "unique user id":None,
    }   
    try:
        user_data = database.from_("userbase").select("email,password,unique_id").execute()
        if user_data.data == []:
            raise ValueError("No user with that email address")
        
        for record in user_data.data:
            # data is considered fully retrieved only if correctly decrypted
            
            retrieved_email = encr_module.decrypt(record['email'])
            if mail == retrieved_email:  
                retrieved_password = encr_module.decrypt(record["password"])
                if retrieved_password == password:
                    status_return["attempt valid"] = True
                    status_return["unique user id"] = encr_module.decrypt(record["unique_id"])

    except Exception as e: # Fail login attempt by default
        print("error: " + e)
        
    finally:
        return ( status_return )

        

# Function to add a new user to the database
def add_new_user(database:Client,mail:str,password:str,username:str):
    try:
        if database == None:
            return("Error with database connection, please try again later...")
        
        for argument in [mail,password,username]: # Sanitification of user-inputs
            if argument == None:
                raise ValueError("Missing arguments")
            
        if check_common_email(database,mail) == True:
            raise ValueError("Account already exists with that email address")
        
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
        
        #print("id: ",chosen_id)
        database.from_("userbase").insert([empty_user_table]).execute()
        return chosen_id
        
    except Exception as e: # Catch any errors and avoid crashing the server
        print(e)
        return None
    
    
# Get order data for user dashboard display
def get_user_order_data(database:Client,unique_id:str):
    try:
        query = database.table("userbase").select("*").execute()
        
        for record in query.data: # check every current record in the database
            retrieved_id = encr_module.decrypt(record['unique_id'])
            if unique_id == retrieved_id:
        
            # if not(query.count == None or query.count == 0): # Check if the query returned any results
                print(query.data)
                user_data = query.data[0]
                
                data_to_return = {
                    "username":encr_module.decrypt(user_data['username']),
                    "email":encr_module.decrypt(user_data['email']),
                    "date_joined":user_data['date_joined'],
                    "orders":None,
                }
                
                decrypted_orders = []
                if user_data['confirmed_orders'] == []: # if the confirmed orders are empty (no orders made by the user), skip the whole section below
                    return data_to_return
                    
                    
                for order_id in user_data['confirmed_orders']: # Users will store order ids in their confirmed_orders field
                    
                    order_id = encr_module.decrypt(order_id) # Decrypt the order id
                    client_order_structure = {
                        "id":order_id,
                        "created_at":None,
                        "order_status":None,
                    }
                    
                    try:
                        query = database.table("orders").select("*").eq("id",order_id).execute()
                        if not(query.count == None or query.count == 0): # Check if the query returned any results
                            order_data = query.data[0]
                            
                            client_order_structure["created_at"] = encr_module.decrypt(order_data['created_at'])
                            client_order_structure["order_status"] = encr_module.decrypt(order_data['status'])
                        
                    except Exception as e:
                        continue # Skip this order if there is an error
                        

                    
                    data_to_return["orders"] = decrypted_orders # Add the decrypted orders to the data to return
                    print(data_to_return)

                    return data_to_return
        
    except Exception as e:
        print("Error: " + str(e))
        return None
    
    
# Function to add an order to the database
def add_order(database:Client,user_unique_id:str,address:str,extra_notes:str,order_items:dict,order_price:float):
    try:
        
        order_table = { # Follows exact structure of 'orders' table in Supabase
            'id': str(encr_module.encrypt(_generate_unique_id_())),
            'created_at':str(datetime.datetime.now()),
            'address_to_deliver':str(encr_module.encrypt(address)),
            'order_details':str(encr_module.encrypt(json.dumps(order_items))),
            'order_notes':str(encr_module.encrypt(extra_notes)),
            'order_price':str(encr_module.encrypt(order_price)),
            'ordered_by_id':str(encr_module.encrypt(user_unique_id)),
        }

        
        for key in order_table:
            if order_table[key] is None:
                raise Exception("Error with data encryption.")
        
        database.from_("orders").insert([order_table]).execute()
        
    except Exception as e:
        print("Error: " + e)
        return False