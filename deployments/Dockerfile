FROM apache/airflow:2.7.1-python3.10

USER airflow

RUN python -m pip install --upgrade pip
RUN pip install feedparser \
    pymongo \
    --no-cache-dir

