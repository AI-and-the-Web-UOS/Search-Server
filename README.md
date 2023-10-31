# Search REST API Server
## Project for AI and the Web
This is a simple Flask application that provides two endpoints to search for similar websites based on vector similarity and to update the number of views for a website. It utilizes MongoDB for data storage and retrieval. This project was part of the course "AI and the Web" at Osnabrück University.
<p align="right">(<a href="#top">back to top</a>)</p>

## 📖 Table of Contents
- [Search REST API Server](#search-rest-api-server)
  - [Project for AI and the Web](#project-for-ai-and-the-web)
  - [📖 Table of Contents](#-table-of-contents)
  - [❓ Why?](#-why)
  - [✨ Features](#-features)
  - [💻 Usage](#-usage)
  - [💾 Structure](#-structure)
  - [🚫 Limitations](#-limitations)
  - [📝 Authors](#-authors)
  - [📎 License](#-license)

## ❓ Why?
To distribute the load of handeling user requests and doing the actual rankings of websites, we decided to split the search process in different application, on the hand, there is the server that handles incoming requests and calculates the vectors. On the other hand, there is the application which has been implemented in this repo, which loads the existing website data from a MongoDB database and matches the entries in this database with the user query, to return optimal results.
<p align="right">(<a href="#top">back to top</a>)</p>

## ✨ Features
The algorithm to determine the optimal ranking of results features to core parts. First, we match the websites title with the user query to find the optimal match purely based on content. Second, we rely on previously collected data by other users to find the best website for the user.</p>

The website selection process on this server, triggered by the '/search' endpoint, operates as follows: It expects a JSON object in the GET request, containing a query vector. The provided query vector is compared to the vector representations of websites stored in the MongoDB collection. Using cosine similarity calculations, the server measures the similarity between the query vector and each stored vector. Websites are then ranked by their similarity to the query vector, and the results are returned as a list of websites and their respective similarity scores. This process enables users to search for websites that are most similar to the provided query vector, which can be a valuable feature for various applications such as content recommendation or similarity-based search.

## Addressing Data Relevance: A Formula for Weighting Views

In various data-driven applications, determining the relevance of data points, such as views or interactions, is a critical challenge. One common scenario involves assessing the importance of such data while considering both the quantity and the recency of those interactions. 

### The Problem:

The challenge lies in appropriately valuing the data points, as not all views are equal, and their relevance change over time. To address this issue, a formula has been devised to calculate a relevance score from views.

### The Formula:

The relevance score formula is as follows:

$$
\
s = \sum_{w=0}^{10} [\frac{1}{w+1} \cdot \frac{1}{1 + e^{(1 - \frac{\text{views}(w)}{10,000} + e)}}] + \frac{1}{11} \cdot \frac{1}{1 + e^{(1 - \frac{\text{views}(<11)}{10,000} + e)}}
\
$$

In this formula, (_w_) represents the week, and $\text{views}(w)\$ is the number of views for that week. The summation considers views over 11 weeks and calculates a relevance score that balances the significance of views based on both their quantity and recency. Additionally, the formula includes a term that includes all even older views, providing further adjustments to the relevance score. This approach is valuable in scenarios where it's essential to prioritize more recent and relevant data while accounting for diminishing importance of older user data, while not completely ignoring the later.

<p align="right">(<a href="#top">back to top</a>)</p>

## 💻 Usage

1. Clone the repository or download the code.

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
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

## 💾 Structure
<!-- Project Structure -->

    .
    │── README.md
    │── requirements.txt
    └── server.py                  # The file containing the actual server
<p align="right">(<a href="#top">back to top</a>)</p>

## 🚫 Limitations
Efficiently managing server loads is a critical aspect of web service optimization. One approach to achieve better load management is to assign specific clusters of websites to individual servers. By leveraging unsupervised clustering techniques on the vector representations of websites stored in the database, we can group similar websites together. Each server would then be responsible for serving requests related to websites within its designated cluster. This strategy ensures that servers are specialized in handling a specific subset of websites, minimizing the risk of overloading and optimizing resource utilization. Additionally, it enhances response times for users as they are directed to servers tailored to their search context. Such an approach not only improves server load management but also enhances the overall performance and scalability of the web service. But due to the scope of the project, this feature was not implemented.
<p align="right">(<a href="#top">back to top</a>)</p>

## 📝 Authors
[Cornelius Wolff](mailto:cowolff@uos.de)<br/>
<p align="right">(<a href="#top">back to top</a>)</p>

## 📎 License
Copyright 2022 Cornelius Wolff

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
