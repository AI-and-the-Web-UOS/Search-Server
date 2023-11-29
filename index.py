import time
import threading
from pymongo import MongoClient

from database import WebsiteDatabase

class IndexUpdater:
    """
    IndexUpdater class manages the background task of updating the index list from the MongoDB database.

    Attributes:
        index_list (list): A list containing all websites from the MongoDB collection.
        mongoDB (str): The URI for connecting to the MongoDB server.
        lock (threading.Lock): A thread lock for ensuring thread safety when updating the index list.

    Methods:
        background_task(): A background task that periodically updates the index list from the MongoDB collection.
    """

    def __init__(self, database_name):
        """
        Initialize the IndexUpdater.

        Args:
            mongoDB (str): The URI for connecting to the MongoDB server.
        """
        self.index_list = []
        # self.mongoDB = mongoDB
        self.database_name = database_name
        self.lock = threading.Lock()

    def background_task(self):
        """
        Periodically update the index list from the MongoDB collection in the background.

        The method establishes a connection to MongoDB, retrieves documents from the 'Website' collection
        in the 'searchDatabase', and updates the index list with simplified representations of the documents.
        If an exception occurs during MongoDB operations, the code attempts to reconnect.

        The method runs indefinitely with a sleep period of one hour between iterations.
        """
        # Establish a MongoDB connection using the provided URI
        print("Connecting to MongoDB....")
        database = WebsiteDatabase(self.database_name)
        # client = MongoClient(self.mongoDB)
        print("Connected")
        # db = client['searchDatabase']
        # websiteCollection = db['Website']

        while True:
            try:
                # Retrieve documents from the 'Website' collection in the 'searchDatabase'
                documents = database.get_all_websites()
                
                # Safely update the index_list within a locked section
                with self.lock:
                    self.index_list = []
                    for document in documents:
                        # Extract relevant fields from each document and create a simplified representation
                        current = {
                            "vector": document['vector'],
                            "url": document['url'],
                            "relevance": document['relevance'],
                            "content": document['content'],
                            "title": document['title'],
                            "date": document['added']
                        }
                        self.index_list.append(current)

            except Exception as e:
                # If an exception occurs during MongoDB operations, attempt to reconnect
                print("Reconnecting with database....")
                database = WebsiteDatabase(self.database_name)
                # client = MongoClient(self.mongoDB)
                print("Conntected")
                # db = client['searchDatabase']
                # websiteCollection = db['Website']

            # Sleep for one hour before the next iteration of the background task
            time.sleep(3600)
