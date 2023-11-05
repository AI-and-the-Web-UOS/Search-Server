from flask import Flask, request, jsonify
from pymongo import MongoClient
import numpy as np
from scipy.spatial.distance import cdist
import math
from datetime import datetime, timedelta
import time
from relevance import *
import threading

app = Flask(__name__)

mongoDB = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2'

# Set up a connection to your MongoDB database
client = MongoClient(mongoDB)
db = client['searchDatabase']
websiteCollection = db['Website']

@app.route('/search', methods=['GET'])
def search():
    # Get the JSON data from the request
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

    query_vector = np.array(data.get("Vector"))

    if not query_vector.any():
        return jsonify({'error': 'No vector provided'}), 400

    # Retrieve documents from the MongoDB websiteCollection
    documents = list(websiteCollection.find())

    # Calculate cosine similarity between the query vector and stored vectors
    results = []
    for document in documents:
        vector = np.array(document['vector'])
        similarity = cdist([query_vector], [vector])[0]
        results.append({
            'website': document['url'],
            'score': similarity.tolist()[0] + document["relevance"],
            'content': document['content'],
            'title': document['title']
        })

    # Sort results by similarity in descending order
    results = sorted(results, key=lambda x: x['score'], reverse=True)

    return jsonify({'results': results})

@app.route('/addView', methods=['POST'])
def add_view():
    # Get the JSON data from the request
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    url = data["site"]
    
    # Get the current week and year
    current_week = datetime.now().isocalendar()[1]
    current_year = datetime.now().year

    # Find the document for the specified URL, current week, and current year
    query = {"url": url, "week": current_week, "year": current_year}
    view_document = db.Views.find_one(query)

    if view_document:
        # If the document exists, increment the "views" field by one
        new_views = view_document["views"] + 1
        db.Views.update_one(query, {"$set": {"views": new_views}})
    else:
        # If the document does not exist, create a new document with views=1
        new_view_document = {
            "url": url,
            "week": current_week,
            "year": current_year,
            "views": 1
        }
        db.Views.insert_one(new_view_document)

    return "", 200

if __name__ == '__main__':
    x = threading.Thread(target=periodic_task, args=(mongoDB,), daemon=True)
    x.start()
    app.run()