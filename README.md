# ELT DuckDB and Metabase

In this project we have a simple ELT using python for extaction and load, [dbt](https://docs.getdbt.com/) for transformation and [DuckDB](https://duckdb.org/) as a lightweight data warehouse. In addition to the ELT we included a free data visualization tool [Metabase]() with a simple report on the gathered data. The process works as follows:

## Set you local environment
First of all, set your local python environment:
```
python -m venv ./.venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Extract and Load
We have a simple python script (`main.py`) which requests the csv from the data source, reads the file in a streaming fashion to not occupy all the memory and then saves to a temporary file locally so it can be loaded by the DuckDB.
To load the file into DuckDB we simply use the native read_csv function and we persist data as a table in the database file.


To execute this process, we create a docker image with the script. In that way we could run it wherever we want (locally, on a lambda function, on a kubernetes pod) and scheduled it however we like it (crontabs, airflow operators, etc.). To run locally just:
- Build the image:
```
docker build -t fire-incidents-ingestion:latest -f ingestion-Dockerfile .
```
- Run the image with a a local volume bind so the DuckDB database will be stored locally (not only in the docker container)
```
docker run -v <full_path_your_local_repository_root>/duck_db:/duck_db fire-incidents-ingestion
```

## Transform
To execute the transformation we use DBT connected on our local DuckDB database. To execute run the following command:
```
dbt run --project-dir=./dbt --profiles-dir=./dbt
```
**Important**: You must first run the extraction and load procedure above, otherwise DBT won't find the local DuckDB file

## Reporting
To to reporting, we span a local instance of Metabase. Metabase is a free data visualization tool that facilitates building reports easily. To get it running, first we must build the metabase image with the DuckDB connector. In addition to it, in the repository we have a metabase database snapshot with a couple users, connection to your local DuckDB database configured and a dashboard with some basic information from fire incidents.

To get it going, do the following:
- Build you metabase image with the DuckDB connector and the DB snapshot
```
docker build -t metaduck:latest -f metaduck-Dockerfile . 
```
- Run the image locally with a volume pointing to ou local DuckDB database:
```
docker run --name metaduck -d -p 80:3000 -m 2GB -e MB_PLUGINS_DIR=/home/plugins -v <full_path_your_local_repository_root>/duck_db:/container/directory metaduck
```

Then you can access metabase through localhost and login using the followinf information:
```
Email address: litogaw263@rohoza.com
Password: Metabase101
```

From there, just click on **Fire Incidents Dash** and check for yourself the following dashboard:
![Dash Example](/assets/img/dash_image.png "Dashboard")
