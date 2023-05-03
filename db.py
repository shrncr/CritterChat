import bson
import os
from flask import current_app, g, Flask
from werkzeug.local import LocalProxy
from flask_pymongo import PyMongo
from flask_pymongo import pymongo
from pymongo.mongo_client import MongoClient 
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from bson.errors import InvalidId
from config import *
import configparser


#get all of the message objects from the alternate pi!
def get_from_other_pi(pi):
    if pi == 0:
        vids=list(db.comments.find( {"sndr":1},{"video":1,"_id":0}   )) #filters out vids sent by other sender
        messages = list(db.comments.find( {"sndr":1}  )) #gets all messages (includes info from vids above)
        
        return(messages,vids)
    elif pi == 1:
        vids=list(db.comments.find( {"sndr":0},{"video":1,"_id":0}   )) 
        messages = list(db.comments.find( {"sndr":0}  )) #not sure if this works <3
        return(messages,vids)
    else:
        return("not good.")

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))

#Creates flask app which connects to db
if __name__ == "__main__":
    app = Flask(__name__)
    app.debug = True
    app.config['MONGO_URI'] = []#put your db info here
    app.run(debug=True)

def add_comment(message, sender):
    comment_doc = { 'video' : message, 'sndr' : sender}
    return db.comments.insert_one(comment_doc) #inserting comment consisting of vid and sender

def delete_comment(comment_id): #deletes comment given comment id
    response = db.comments.delete_one( { "_id": ObjectId(comment_id) } )
    return response


# to put onto github
import requests
# for encoding
import base64

#API token
githubToken = "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"

#posts media to github and returns the link to the file's location in the repo
def putMedia(mediaName):
    githubAPIURL = "https://api.github.com/repos/shrncr/Media/contents/{}".format(mediaName)
    with open(mediaName, "rb") as f:
        # Encoding "my-local-image.jpg" to base64 format
        encodedData = base64.b64encode(f.read())
        
        headers = {
            "Authorization": f'''Bearer {githubToken}''',
            "Content-type": "application/vnd.github+json"
        }
        data = {
            "message": "Pi One", # Put your commit message here.
            "content": encodedData.decode("utf-8")
        }

        r = requests.put(githubAPIURL, headers=headers, json=data)
        
        print(r.content)
    return("https://github.com/shrncr/Media/blob/main/{}".format(mediaName))


