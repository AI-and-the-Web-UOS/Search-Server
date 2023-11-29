import sqlite3
from datetime import datetime
import json

class WebsiteDatabase:
    def __init__(self, db_name='data.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Create 'Website' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Website (
                title TEXT,
                content TEXT,
                added DATE,
                url TEXT PRIMARY KEY,
                vector TEXT,
                relevance REAL
            )
        ''')

        # Create 'Views' table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Views (
                url TEXT,
                week INTEGER,
                year INTEGER,
                views INTEGER,
                FOREIGN KEY (url) REFERENCES Website(url)
            )
        ''')

        self.conn.commit()

    def insert_website(self, title, content, added, url, vector, relevance):
        self.cursor.execute('''
            INSERT INTO Website (title, content, added, url, vector, relevance)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, content, added, url, vector, relevance))
        self.conn.commit()

    def insert_view(self, url, week, year, views):
        self.cursor.execute('''
            INSERT INTO Views (url, week, year, views)
            VALUES (?, ?, ?, ?)
        ''', (url, week, year, views))
        self.conn.commit()

    def get_website(self, url):
        self.cursor.execute('''
            SELECT * FROM Website WHERE url = ?
        ''', (url,))
        return self.cursor.fetchone()

    def get_all_websites(self):
        self.cursor.execute('''
            SELECT * FROM Website
        ''')
        websites = []
        for row in self.cursor.fetchall():
            website = {
                'title': row[0],
                'content': row[1],
                'added': row[2],
                'url': row[3],
                'vector': row[4],
                'relevance': row[5]
            }
            websites.append(website)
        return websites
    
    def get_all_views(self):
        self.cursor.execute('''
            SELECT * FROM Views
        ''')
        views = []
        for row in self.cursor.fetchall():
            view = {
                'url': row[0],
                'week': row[1],
                'year': row[2],
                'views': row[3]
            }
            views.append(view)
        return views
    
    def get_views_for_website(self, url):
        self.cursor.execute('''
            SELECT week, year, views FROM Views WHERE url = ?
        ''', (url,))
        views = self.cursor.fetchall()

        # Convert the result to a list of dictionaries
        views_with_dicts = []
        for view in views:
            week, year, views_count = view
            view_dict = {
                'week': week,
                'year': year,
                'views': views_count
            }
            views_with_dicts.append(view_dict)

        return views_with_dicts
    
    def update_website_relevance(self, url, relevance_score):
        self.cursor.execute('''
            UPDATE Website SET relevance = ? WHERE url = ?
        ''', (relevance_score, url))
        self.conn.commit()
    
    def find_one_view(self, url, week, year):
        self.cursor.execute('''
            SELECT * FROM Views WHERE url = ? AND week = ? AND year = ?
        ''', (url, week, year))
        view = self.cursor.fetchone()

        return view
    
    def update_views(self, url, week, year, new_views):
        self.cursor.execute('''
            UPDATE Views SET views = ? WHERE url = ? AND week = ? AND year = ?
        ''', (new_views, url, week, year))
        self.conn.commit()

    def insert_or_update_view(self, url, week, year):
        view_document = self.find_one_view(url, week, year)

        if view_document:
            # If the view document exists, update the views
            new_views = view_document[3] + 1  # Assuming the 'views' column is at index 3
            self.update_views(url, week, year, new_views)
        else:
            # If the view document doesn't exist, insert a new one
            self.insert_view(url, week, year, 1)
    
    def insert_website(self, title, content, added, url, vector, relevance):
        # Serialize the vector to a JSON string before storing in the database
        vector_json = json.dumps(vector)
        try:
            self.cursor.execute('''
                INSERT INTO Website (title, content, added, url, vector, relevance)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, content, added, url, vector_json, relevance))
        except sqlite3.IntegrityError:
            print(f'Website {url} already exists in the database')
        self.conn.commit()

    def insert_data(self, data_list):
        for data in data_list:
            title = data.get('title', '')
            content = data.get('content', '')
            added = data.get('added', datetime.now())
            url = data.get('url', '')
            vector = data.get('vector', [])
            relevance = data.get('relevance', 0.0)

            self.insert_website(title, content, added, url, vector, relevance)

    def get_all_websites(self):
        self.cursor.execute('''
            SELECT title, content, added, url, vector, relevance FROM Website
        ''')
        websites = self.cursor.fetchall()

        # Convert the vector from JSON to a Python list
        websites_with_dicts = []
        for website in websites:
            title, content, added, url, vector_json, relevance = website
            vector = json.loads(vector_json)

            website_dict = {
                'title': title,
                'content': content,
                'added': added,
                'url': url,
                'vector': vector,
                'relevance': relevance
            }

            websites_with_dicts.append(website_dict)

        return websites_with_dicts

    def close_connection(self):
        self.conn.close()