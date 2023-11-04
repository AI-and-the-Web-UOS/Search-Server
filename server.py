from flask import Flask, request, jsonify
from pymongo import MongoClient
import numpy as np
from scipy.spatial.distance import cdist
import math
from datetime import datetime, timedelta
import time
from relevance import *

app = Flask(__name__)

# Set up a connection to your MongoDB database
client = MongoClient('mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2')
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
            'similarity': similarity.tolist()
        })

    # Sort results by similarity in descending order
    results = sorted(results, key=lambda x: x['similarity'], reverse=True)

    return jsonify({'results': results})

@app.route('/addView', methods=['POST'])
def add_view():
    # Get the JSON data from the request
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    site_title = data["site"]
    site_document = websiteCollection.find_one({'URL': site_title})

    if site_document:
        
        # Retrieves the current views
        current_views = site_document.get('Views', 0)

        # Increase number of views plus one
        new_views = current_views + 1

        # Update values in the mongoDB database
        websiteCollection.update_one(
            {'Title': site_title},
            {'$set': {'Views': new_views}}
        )
    else:
        print("Website not found")

    return "", 200

if __name__ == '__main__':
    app.run()