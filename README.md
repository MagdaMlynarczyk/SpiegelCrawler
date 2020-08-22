## SpiegelCrawler

#### Deployment instruction:
```
git clone https://github.com/MagdaMlynarczyk/SpiegelCrawler.git
cd SpiegelCrawler
docker-compose build
docker-compose up -d
```

#### Notes:
1. The solution contains of tho main components: Flask API and Elasticsearch Database. Both of them are deployed with docker.

2. *Kibana* is an additional component. I've used it during the development process. Now it can 
be useful for browsing the SpiegelCrawler results.

3. In my solution I have decided to use an article url as an article id. 
If the url changes for an article, the new document will be saved to Elasticsearch.

4. Accessing the log file:
```
docker exec -it spiegel-crawler bash
cat crawler.logs
```
