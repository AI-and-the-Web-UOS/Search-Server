import time
import threading
from pymongo import MongoClient

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

    def __init__(self, mongoDB):
        """
        Initialize the IndexUpdater.

        Args:
            mongoDB (str): The URI for connecting to the MongoDB server.
        """
        self.index_list = []
        self.mongoDB = mongoDB
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
        client = MongoClient(self.mongoDB)
        db = client['searchDatabase']
        websiteCollection = db['Website']

        while True:
            try:
                # Retrieve documents from the 'Website' collection in the 'searchDatabase'
                documents = list(websiteCollection.find())
                
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
                            "title": document['title']
                        }
                        self.index_list.append(current)

            except Exception as e:
                # If an exception occurs during MongoDB operations, attempt to reconnect
                client = MongoClient(self.mongoDB)
                db = client['searchDatabase']
                websiteCollection = db['Website']

            # Sleep for one hour before the next iteration of the background task
            time.sleep(3600)
