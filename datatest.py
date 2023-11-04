import pandas as pd
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
import copy

def testDatabase():
    # Connect to MongoDB
    client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2")
    db = client.searchDatabase

    # Define the end date for the last 10 weeks
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=10)

    # Define a function to aggregate views for each website
    def aggregate_views(website):
        views_cursor = db.Views.find({
            "url": website["url"],
            "week": {"$gte": start_date.isocalendar()[1], "$lte": end_date.isocalendar()[1]},
            "year": {"$in": [start_date.year, end_date.year]}
        })
        total_views = 0
        for view in views_cursor:
            total_views += view["views"]
        return total_views

    # Retrieve all websites
    websites_cursor = db.Website.find({})
    websites_data = []

    # Iterate through the websites and aggregate views
    for website in websites_cursor:
        total_views = aggregate_views(website)
        websites_data.append({
            "title": website["title"],
            "content": website["content"],
            "added": website["added"],
            "url": website["url"],
            "total_views_last_10_weeks": total_views
        })

    # Create a Pandas DataFrame
    df = pd.DataFrame(websites_data)

    # Display the DataFrame
    print(df)

def get_last_weeks(website_url):
    client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2")
    db = client.searchDatabase
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=10)

    # Query for views within the last 10 weeks for the specified website
    views_data = db.Views.find({
        "url": website_url
    })

    # Print the retrieved views data
    for view in views_data:
        print("Week:", view["week"])
        print("Year:", view["year"])
        print("Views:", view["views"])
        print()
    client.close()

def addTestData():
    # Connect to MongoDB
    client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2")
    db = client.searchDatabase 

    # Define the start date (previous year) and current date
    start_date = datetime(datetime.now().year - 1, 1, 1)
    end_date = datetime.now()
    # Insert the sample data into the "Views" collection

    sample_data = [
        {
            "title": "Example Website 1",
            "content": "This is some content for the first website.",
            "added": datetime(2023, 11, 5, 0, 0),
            "url": "https://www.example.com",
            "vector": [1.2, 3.4, 5.6],
            "relevance": 0.75
        },
        {
            "title": "Example Website 2",
            "content": "This is some content for the second website.",
            "added": datetime(2023, 11, 5, 0, 0),
            "url": "https://www.example2.com",
            "vector": [2.3, 4.5, 6.7],
            "relevance": 0.88
        },
    ]

    # Insert the sample data into the "Website" collection
    db.Website.insert_many(sample_data)

    # Sample data to insert
    sample_data = {
        "url": "https://www.example.com",
        "week": 45,
        "year": 2023,
        "views": 1000
    }

    # Loop to insert data for each week within the date range
    data = []
    current_date = start_date
    while current_date <= end_date:
        current_data = copy.deepcopy(sample_data)
        week_number = current_date.isocalendar()[1]
        current_data["year"] = current_date.year
        current_data["week"] = week_number
        data.append(current_data)

        current_date += timedelta(weeks=1)
    db.Views.insert_many(data)

    # Close the MongoDB connection
    client.close()

addTestData()
# testDatabase()