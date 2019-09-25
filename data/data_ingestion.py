import os
from google.cloud import bigquery
import pandas as pd
import numpy as np
import psycopg2
import click
import tqdm
from decouple import config


# Elephant DB connection info
"""
dbname = config('ESQL_R2_DBNAME')
user = config('ESQL_R2_USER')
password = config('ESQL_R2_PASSWORD')
host = config('ESQL_R2_HOST')
"""

# AWS DB connection info
dbname = config('RDS_1_DBNAME')
user = config('RDS_1_USER')
password = config('RDS_1_PASSWORD')
host = config('RDS_1_HOST')

# Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config('GOOGLE_APPLICATION_CREDENTIALS')

def pull_rows(client, dref, table_name, start_index=0, count=40000):
    """
    Query count rows starting at index from table_name in dataset of 
    established bigquery client

    client: bigquery client connection
    dref: bigquery dataset reference
    table_name: bigquery dataset table name
    start_index: starting index of query
    count: how many rows to query

    Returns a list of bigquery row instances
    """
    table_ref = dref.table(table_name)
    table = client.get_table(table_ref)
    results = [x for x in client.list_rows(table, start_index=start_index, max_results=count)]

    return results

def get_tables(client, dataset):
    """
    Get the names of all tables in a bigquery dataset.

    client: bigquery connection
    dataset: a connected bigquery dataset

    Returns a list of all tables in the dataset
    """
    return [table.table_id for table in client.list_tables(dataset)]

def row_counts(client, dataset, table_name):
    """
    Get the row count for a specified table

    client: bigquery connection
    dataset: a connected bigquery dataset
    table_name: name of the table

    Returns a count of the number of rows in a table
    """
    table = client.get_table(dataset.table(table_name))
    row_count = table.num_rows

    return row_count

def data_ingestion(table_name, rows):
    """
    Ingest list of bigquery rows into postgres DB
    ***ONLY USE ON COMMENTS TABLE OF HACKER NEWS DATASET***

    rows: list of bigquery row instances

    No output
    """
    conn = psycopg2.connect(dbname=dbname, user=user,
                            password=password, host=host)

    curs = conn.cursor()

    # Add single quotes to values - otherwise SQL thinks they're columns
    # Non-integer columns should be converted to strings
    # Boolean deleted & dead columns should be converted to numeric
    for r in tqdm.tqdm(rows):
        keys = list(r.keys())
        values = list(r.values())
        
        values[1] = "'"+str(values[1])+"'"
        values[2] = "'"+str(values[2])+"'"
        values[4] = "TO_TIMESTAMP('"+str(values[4])+"', 'yyyy-mm-dd hh24:mi:ss')"
        values[5] = "'"+str(values[5]).replace('"', '""').replace("'", "''")+"'"
        values[6] = "0" if str(values[6]) == "None" else str(values[6])
        values[7] = "'0'" if str(values[7]) == "None" else "'1'"
        values[8] = "'0'" if str(values[8]) == "None" else "'1'"

        insert_record = f'''
            INSERT INTO {table_name} ( 
                {', '.join(str(k) for k in keys)}
            )
            VALUES (
                {', '.join(str(v) for v in values)}
            );
        '''
        curs.execute(insert_record)

    curs.close()
    conn.commit()
    conn.close()


@click.command()
@click.option('--counts', default=False, help='Return total number of rows in a table')
@click.option('--start', default=0, help='Starting row of data to be pulled')
@click.option('--rows', default=10000, help='')
def run_query(counts, start, rows):
    """
    Run a query of the Hacker News database using Google's
    Big Query API.

    https://www.kaggle.com/sohier/beyond-queries-exploring-the-bigquery-api
    """
    client = bigquery.Client()
    hn_ref = client.dataset('hacker_news', project='bigquery-public-data')
    hn_dataset = client.get_dataset(hn_ref)

    if counts:
        row_count = row_counts(client, hn_dataset, 'comments')
        print('{} rows in comments table'.format(row_count))

if __name__ == '__main__':
    run_query()