from flask import Flask, request, jsonify
from pymongo import MongoClient
import numpy as np
from scipy.spatial.distance import cdist
import math
from datetime import datetime, timedelta

app = Flask(__name__)

# Set up a connection to your MongoDB database
client = MongoClient('mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2')
db = client['searchDatabase']
websiteCollection = db['Website']

def get_last_weeks(website_url):
    # Query for views within the last 10 weeks for the specified website
    views_data = db.Views.find({
        "url": website_url,
    })

    # Print the retrieved views data
    views = []
    for view in views_data:
        views.append(view["views"]) 
    return reversed(views)

def calculate_relevance_score(views):
    relevance_score = 0

    # Loop through the first 11 weeks
    for w in range(11):
        # Calculate the 'w_term' which is 1 / (w + 1)
        w_term = 1 / (w + 1)

        # Get the number of views for the current week 'w'
        views_w = views[w] if w < len(views) else 0

        # Calculate the 'e_term' which involves exponential calculations based on the views
        e_term = 1 / (1 + math.exp(1 - (views_w / 10000) + math.e))

        # Add the product of 'w_term' and 'e_term' to the relevance score
        relevance_score += w_term * e_term

    # Calculate the sum of views for weeks beyond the first 11 weeks (older views)
    older_views = sum(views[11:])
    older_term = 1 / 11 * (1 / (1 + math.exp(1 - (older_views / 10000) + math.e)))
    relevance_score += older_term
    return relevance_score

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