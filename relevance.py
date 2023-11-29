from flask import Flask, request, jsonify
from pymongo import MongoClient
import numpy as np
from scipy.spatial.distance import cdist
import math
from datetime import datetime, timedelta
import time

from database import WebsiteDatabase

def get_last_weeks(db, website_url):
    # Query for views within the last 10 weeks for the specified website
    # views_data = db.Views.find({
    #     "url": website_url,
    # })

    # Get the current date
    views_data = db.get_views_for_website(website_url)

    # Add the views to a list
    views = []
    for view in views_data:
        views.append(view["views"]) 
    return list(reversed(views))

# Define a function to update the relevance score for all websites
def updateRelevanceScores(db):

    # Retrieve all websites from the "Website" collection
    websites = db.get_all_websites()

    # Calculate and update the relevance score for each website
    for website in websites:
        url = website["url"]
        data = get_last_weeks(db, url)
        relevance_score = float(calculate_relevance_score(data))
        # Update the relevance field in the database
        db.update_website_relevance(url, relevance_score)

# Define a function to run the update task periodically
def periodic_task(database_name):
    # Connect to MongoDB
    # client = MongoClient(mongoDB) 
    # db = client.searchDatabase
    db = WebsiteDatabase(database_name)
    while True:
        try:
            updateRelevanceScores(db)
            time.sleep(3600)  # Sleep for one hour (3600 seconds)
        except:
            # client.close()
            print("Could not update relevance score")
            time.sleep(60)
            # client = MongoClient(mongoDB)
            db = WebsiteDatabase(database_name)
            # db = client.searchDatabase

def calculate_relevance_score(views):
    relevance_score = 0

    # Loop through the first 11 weeks
    for w in range(min(11, len(views))):
        # Calculate the 'w_term' which is 1 / (w + 1)
        w_term = 1 / (w + 1)

        # Get the number of views for the current week 'w'
        views_w = views[w] if w < len(views) else 0

        # Calculate the 'e_term' which involves exponential calculations based on the views
        e_term = 1 / (1 + math.exp(1 - (views_w / 10000) + math.e))

        # Add the product of 'w_term' and 'e_term' to the relevance score
        relevance_score += w_term * e_term

    # Calculate the sum of views for weeks beyond the first 11 weeks (older views)
    if len(views) > 10:
        older_views = sum(views[11:])
        older_term = 1 / 11 * (1 / (1 + math.exp(1 - (older_views / 10000) + math.e)))
        relevance_score += older_term
    return relevance_score