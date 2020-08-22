FROM python:3.7

RUN mkdir crawler
WORKDIR crawler

COPY ["requirements.txt", "./"]

RUN pip install -r requirements.txt

COPY ["app.py", \
    "config.json", \
    "config.py", \
    "./"]

RUN mkdir utils
COPY ["utils/crawler.py", \
    "utils/elastic.py", \
    "./utils/"]

CMD ['bash']
