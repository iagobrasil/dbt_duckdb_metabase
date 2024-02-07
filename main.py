import requests
import tempfile
import duckdb
from math import ceil
import logging
import logging.config


log = logging.getLogger(__name__)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def copy_file_to_duck_db():
    page_size = 10000
    resp = requests.get('https://data.sfgov.org/resource/wr8u-xric.csv?$select=COUNT(*)')
    total_rows = int(resp.text.split("\n")[1].replace('"', ''))
    log.info(f"Going to read {total_rows} incidents from San Francisco data")
    with tempfile.NamedTemporaryFile("wb") as file:
        for i in range(ceil(total_rows/page_size)):
            log.info(f"Getting page {i+1} of {ceil(total_rows/page_size)}")
            with requests.get(f'https://data.sfgov.org/resource/wr8u-xric.csv?$offset={page_size*i}&$limit={page_size}&$order=:id', stream=True) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
        with duckdb.connect('duck_db/incidents.db') as con:
            schema = open('fire_incident_schema').read()
            log.info("Creating table in duckdb Database")
            newline = "\n"
            con.sql(f"CREATE OR REPLACE TABLE raw_fire_incidents AS SELECT * FROM read_csv('{file.name}', columns = {schema.replace(newline, ' ')}, header=1, ignore_errors=TRUE);")

if __name__ == '__main__':
    copy_file_to_duck_db()
