from datetime import datetime, timedelta
import json 

def load_data(file_name: str):
    with open(file_name, 'r') as file:
        return json.load(file) 
    
def save_data(file_name:str,data):
    with open(file_name,"w") as file:
        json.dump(data,file, indent=4)