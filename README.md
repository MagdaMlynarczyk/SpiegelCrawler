## SpiegelCrawler

#### Deployment instruction:
```
git clone https://github.com/MagdaMlynarczyk/SpiegelCrawler.git
cd SpiegelCrawler
docker-compose build
docker-compose up -d
```

#### Solution description:
The solution consists of two main components: a Flask application and an Elasticsearch Database. 
Both of them are deployed with docker.

I have chosen Elasticsearch as the adequate database because it is an open-source solution for managing text data. 
Moreover, there is an official client for Python. For bigger project it has also the advantage of being distributed.

At the beginning, it is being checked if the relevant index in the database exists. If not, it is being created.

Secondly, the flask application calls the crawl method of the SpiegelCrawler class. 
It crawls the www.spiegel.de/international webpage and search for articles abstracts on it.
It extracts all the metadata relevant to the task: the article title, header (a text that appears
below or above the title with smaller font), the abstract, the url of the target article and the timestamp of when it was called.

In my solution I have decided to use an article url as the article id. 

Next, the save_data of the ElasticConnector is called. The ElasticConnector class allows to communicate with the database.
For each crawled article it checks if it has already been saved in the database - based on the article id. If yes, the article is
not being loaded to the database again, only the 'update-time' attribute of the document is being updated to the current crawling timestamp.
Otherwise the whole metadata of the article is being saved to the Elasticsearch 

The pipeline of crawling the data and updating the database is being scheduled to run automatically every 15 minutes (the time interval
between the calls can be easily changed in the config file)

Notes:

1. If the url changes for an article, the new document will be saved to Elasticsearch.

2. *Kibana* is an additional component. I've used it during the development process. Now it can 
be useful for browsing the SpiegelCrawler results.

3. I have not deployed the solution using a web server like WSGI/Gunicorn, although it would be necessary in a production solution.

4. Given more time I would cover the codebase with unit/integration tests with mocked requests.

5. 4GB of RAM might be required to run the application.

#### Useful commands:
##### Accessing the log file:
```
docker exec -it spiegel-crawler bash
cat crawler.logs
```

##### Example of searching for an article using Kibana Dev Tools:
Based on the article header:
```
GET spiegel-international-news/_search
{
  "query": {
    "match_phrase": {
      "header":  "movies in misery"
    }
  }
}
```
Note, that the match_phrase query in case-insensitive.

Analogously, a search for the article based on article title
```
GET spiegel-international-news/_search
{
  "query": {
    "match_phrase": {
      "title": "Cutting Corners in the Race for a Vaccine"
    }
  }
}
```

A search for the article based on id:
```
GET spiegel-international-news/_search
{
  "query": {
    "terms": {
      "_id": ["https://www.spiegel.de/international/germany/tempers-flare-over-german-mask-requirement-a-3edea99d-3563-43e6-8401-4671a6671816"]
    }
  }
}
```

Moreover, we can search for the articles whose abstracts are most similar to what we are looking for.
For example, if we want to find any information about "pandemic influence on the climate", we can search for the article whose abstract matches to our query:
```
GET spiegel-international-news/_search
{
  "query": {"match": {
    "abstract": "pandemic influence on the climate"
  }}}
```
The article with the highest score is - at the moment of writing it :) - "Assault on the Rainforest Continues in the Shadow of the Pandemic".