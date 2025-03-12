from datetime import datetime, timedelta
import json 

#file to store library data 
FILE_NAME="library_data.json"


data = {"Book":[],"Member":[],"Admin":[],"Borrow_Books":[]}
    

def load_data():
    try:
        with open(FILE_NAME,"r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"Book":[],"Member":[],"Admin":[],"Borrow_Books":[]}
        
def save_data(data):
    with open("library_data.json","w") as file:
        json.dump(data,file, indent=4)