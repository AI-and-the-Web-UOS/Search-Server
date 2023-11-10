# Search REST API Server
## Project for AI and the Web
This is a simple Flask application that provides two endpoints to search for similar websites based on vector similarity and to update the number of views for a website. It utilizes MongoDB for data storage and retrieval. This project was part of the course "AI and the Web" at Osnabrück University.
<p align="right">(<a href="#top">back to top</a>)</p>

## 📖 Table of Contents
- [Search REST API Server](#search-rest-api-server)
  - [Project for AI and the Web](#project-for-ai-and-the-web)
  - [📖 Table of Contents](#-table-of-contents)
  - [❓ Why?](#-why)
  - [✨ Features of the search server](#-features-of-the-search-server)
    - [Cosine Similarity for Ranking Web Search Results](#cosine-similarity-for-ranking-web-search-results)
      - [Cosine Similarity Formula](#cosine-similarity-formula)
      - [Vector Ordering by Cosine Similarity](#vector-ordering-by-cosine-similarity)
    - [Addressing Data Relevance: A Formula for Weighting Views](#addressing-data-relevance-a-formula-for-weighting-views)
      - [The Problem](#the-problem)
      - [The Formula](#the-formula)
  - [💻 Usage](#-usage)
  - [📖 API Documentation](#-api-documentation)
  - [💾 Structure](#-structure)
  - [🚫 Limitations](#-limitations)
  - [📝 Authors](#-authors)
  - [📎 License](#-license)

## ❓ Why?
To distribute the load of handeling user requests and doing the actual rankings of websites, we decided to split the search process in different application. On the one hand, there is the server that handles incoming requests and calculates the vectors. On the other hand, there is the application which has been implemented in this repo, which loads the existing website data from a MongoDB database and matches the entries in this database with the user query, to return optimal results. Lastly there is the web crawler that updates the search index database.
<br/> 
<p align="center">
<img src="graphics/SearchEngine.png" alt="Structure of our search engine" align="middle" width="700" /> 
</p>
<br/> 
<p align="right">(<a href="#top">back to top</a>)</p>

## ✨ Features of the search server
The algorithm to determine the optimal ranking of results features two core parts. First, we match the websites title with the user query to find the optimal match purely based on content. Second, we rely on previously collected data by other users to find the best website for the user.</p>

The website selection process on this server, triggered by the '/search' endpoint, operates as follows: It expects a JSON object in the GET request, containing a query vector. The provided query vector is compared to the vector representations of websites stored in the MongoDB collection. Using cosine similarity calculations, the server measures the similarity between the query vector and each stored vector. Websites are then ranked by their similarity to the query vector, and the results are returned as a list of websites and their respective similarity scores. This process enables users to search for websites that are most similar to the provided query vector, which can be a valuable feature for various applications such as content recommendation or similarity-based search.

In order to circumvent any negative performance impacts by having to access the database every time the API is called, we decided to implement a background thread that updates an index list every hour from the database. As this index list is stored in the RAM, the performance should be much better compared to loading the data from the mongoDB instance, which stores its data on the hard drive. The same principle applies to the calculation of the relevance score based on past views. As looking up all views for each website during every API call results in a very bad runtime, we decided to implement a second background thread that updates the view based relevance of a website every hour.

Next, we will list the two main algorithms determining the relevance of a website to a specific search prompt.

### Cosine Similarity for Ranking Web Search Results

Cosine similarity is a valuable technique for ranking the results of a web search query, as the websites titles are converted into vectors using NLP-models (sent2vec). It measures the similarity between two vectors, providing a way to determine how closely a web page's title aligns with the user's search query. This is particularly effective because it considers the direction and magnitude of vectors, allowing for a more nuanced comparison.

#### Cosine Similarity Formula

$$
\text{Cosine Similarity}(\mathbf{v}, \mathbf{u}) = \frac{\mathbf{v} \cdot \mathbf{u}}{\|\|\mathbf{v}\|\| \|\|\mathbf{u}\|\|}
$$

- `v * u` represents the dot product of vectors `v` and `u`.
- `||v||` represents the L2 norm (magnitude) of vector `v`.
- `||u||` represents the L2 norm (magnitude) of vector `u`.

#### Vector Ordering by Cosine Similarity
To rank search results, sort website titles represented as vectors {v₁, v₂, ..., vₖ} by their cosine similarity to the user's query vector `t`. The ordering is done in descending order based on the similarity value:

```
Sort vectors {v₁, v₂, ..., vₖ} by S(vᵢ, t) in descending order:

vᵢ₁, vᵢ₂, ..., vᵢₖ

Where S(vᵢ₁, t) ≥ S(vᵢ₂, t) ≥ ... ≥ S(vᵢₖ, t).
```

This technique is powerful because it enables search engines to retrieve and present web pages with titles most relevant to the user's query, providing a more accurate and personalized search experience.

### Addressing Data Relevance: A Formula for Weighting Views

In various data-driven applications, determining the relevance of data points, such as views or interactions, is a critical challenge. One common scenario involves assessing the importance of such data while considering both the quantity and the recency of those interactions. 

#### The Problem

The challenge lies in appropriately valuing the data points, as not all views are equal, and their relevance change over time. To address this issue, a formula has been devised to calculate a relevance score from views.

#### The Formula

The relevance score formula is as follows:

$$
\
s = \sum_{w=0}^{10} [\frac{1}{w+1} \cdot \frac{1}{1 + e^{(1 - \frac{\text{views}(w)}{10,000} + e)}}] + \frac{1}{11} \cdot \frac{1}{1 + e^{(1 - \frac{\text{views}(>10)}{10,000} + e)}}
\
$$

In this formula, (_w_) represents the week, and $\text{views}(w)\$ is the number of views for that week. The summation considers views over 11 weeks and calculates a relevance score that balances the significance of views based on both their quantity and recency. Additionally, the formula includes a term that includes all even older views, providing further adjustments to the relevance score. This approach is valuable in scenarios where it's essential to prioritize more recent and relevant data while accounting for diminishing importance of older user data, while not completely ignoring the later.

<p align="right">(<a href="#top">back to top</a>)</p>

## 💻 Usage

1. Clone the repository or download the code.

```bash
git clone https://github.com/AI-and-the-Web-UOS/Search-Server/
cd Search-Server
```

2. Install the required Python packages.

```bash
pip install requirements.txt
```

3. Set up your MongoDB server and replace the connection details in the code with your own.

4. Start the Flask application.

```bash
python server.py
```

The Flask application will run locally on `http://127.0.0.1:5000/`.
<p align="right">(<a href="#top">back to top</a>)</p>

## 📖 API Documentation

<!-- omit in toc -->
### Search Endpoint

`GET /search`

This endpoint allows users to perform a search based on a provided vector. The search results are returned in JSON format, sorted by relevance.

<!-- omit in toc -->
#### Request
- Method: `GET`
- Content-Type: `application/json`

<!-- omit in toc -->
#### Content
- `Vector` (required): An array representing the vector for the search query.

<!-- omit in toc -->
#### Example Request

GET /search
```json
{
  "Vector": [0.1, 0.5, 0.3]
}
```

<!-- omit in toc -->
#### Response
- Content-Type: `json`
- A list of search results containing website information, relevance scores, and content details.

<!-- omit in toc -->
#### Example Response
```json
{
  "results": [
    {
      "website": "https://example.com",
      "score": 0.87,
      "content": "Lorem ipsum...",
      "title": "Example Website"
    },
    {
      "website": "https://another.com",
      "score": 0.76,
      "content": "Dolor sit amet...",
      "title": "Another Website"
    }
    // ... other results
  ]
}
```

<p align="right">(<a href="#top">back to top</a>)</p>
<!-- omit in toc -->
### Add View Endpoint

`POST /addView`

This endpoint allows users to increment the view count for a specified website. The response is an empty body with a status code of 200.

<!-- omit in toc -->
#### Request
- Method: `POST`
- Content-Type: `json`

<!-- omit in toc -->
#### Content
- `site` (required): The URL of the website for which views should be added.

<!-- omit in toc -->
#### Example Request
POST /addView
```json
{
  "site": "https://example.com"
}
```
<!-- omit in toc -->
#### Response
- An empty response body.

<p align="right">(<a href="#top">back to top</a>)</p>

## 💾 Structure
<!-- Project Structure -->

    .
    │── graphics
    │     └── SearchEngine.png
    │── searchDatabase
    │     ├── Views.bson           # Example data for the views table
    │     └── Website.bson         # Example data for the Website table
    │── index.py                   # Contains class, that updates the index in the background
    │── README.md
    │── requirements.txt
    │── commands.txt               # Commands to set up the database
    │── relevance.py               # Contains the calculations for the view based relevance
    └── server.py                  # The file containing the actual server
<p align="right">(<a href="#top">back to top</a>)</p>

## 🚫 Limitations
Efficiently managing server loads is a critical aspect of web service optimization. One approach to achieve better load management is to assign specific clusters of websites to individual servers. By leveraging unsupervised clustering techniques on the vector representations of websites stored in the database, we can group similar websites together. Each server would then be responsible for serving requests related to websites within its designated cluster. This strategy ensures that servers are specialized in handling a specific subset of websites, minimizing the risk of overloading and optimizing resource utilization. Additionally, it enhances response times for users as they are directed to servers tailored to their search context. Such an approach not only improves server load management but also enhances the overall performance and scalability of the web service. But due to the scope of the project, this feature was not implemented.
<p align="right">(<a href="#top">back to top</a>)</p>

## 📝 Authors
[Cornelius Wolff](mailto:cowolff@uos.de) (main maintainer of the repo)<br/>
[Christine Arnold](mailto:carnoldt@uni-osnabrueck.de)<br/>
[Jonah Schlie](mailto:jschlie@uni-osnabrueck.de)<br/>

<p align="right">(<a href="#top">back to top</a>)</p>

## 📎 License
Copyright 2022 Cornelius Wolff, Christine Arnold, Jonah Schlie

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
<p align="right">(<a href="#top">back to top</a>)</p>
