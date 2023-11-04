from flask import Flask, request, jsonify
from pymongo import MongoClient
import numpy as np
from scipy.spatial.distance import cdist
import math
from datetime import datetime, timedelta
import time

def get_last_weeks(db, website_url):
    # Query for views within the last 10 weeks for the specified website
    views_data = db.Views.find({
        "url": website_url,
    })

    # Print the retrieved views data
    views = []
    for view in views_data:
        views.append(view["views"]) 
    return reversed(views)

# Define a function to update the relevance score for all websites
def updateRelevanceScores(db):

    # Retrieve all websites from the "Website" collection
    websites = db.Website.find({})

    # Calculate and update the relevance score for each website
    for website in websites:
        url = website["url"]
        data = get_last_weeks(db, url)
        relevance_score = calculate_relevance_score(data)
        # Update the relevance field in the database
        db.Website.update_one({"_id": website["_id"]}, {"$set": {"relevance": relevance_score}})

# Define a function to run the update task periodically
def periodic_task():
    # Connect to MongoDB
    client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2") 
    db = client.searchDatabase
    while True:
        updateRelevanceScores(db)
        time.sleep(3600)  # Sleep for one hour (3600 seconds)

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