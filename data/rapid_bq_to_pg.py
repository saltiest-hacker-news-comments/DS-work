from google.cloud import bigquery
from sqlalchemy import create_engine
from io import StringIO
import csv
import numpy as np
import os
from decouple import config
from score_update import sentiment_score
import tqdm


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config('GOOGLE_APPLICATION_CREDENTIALS')

client = bigquery.Client()
hn_dataset_ref = client.dataset('hacker_news', project='bigquery-public-data')
comment_ref = hn_dataset_ref.table('comments')
comments = client.get_table(comment_ref)

engine = create_engine('postgres://<user>:<password>@<host>:5432/<dbname>')

def psql_insert_copy(table, conn, keys, data_iter):
    """Uses postgres insert method to convert a dataframe to a csv and
    copy directly into a sql table. Refs:
    https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-sql-method
    https://www.postgresql.org/docs/current/static/sql-copy.html
    """
    # gets a DBAPI connection that can provide a cursor
    dbapi_conn = conn.connection
    with dbapi_conn.cursor() as cur:
        s_buf = StringIO()
        writer = csv.writer(s_buf)
        writer.writerows(data_iter)
        s_buf.seek(0)

        columns = ', '.join('"{}"'.format(k) for k in keys)
        if table.schema:
            table_name = '{}.{}'.format(table.schema, table.name)
        else:
            table_name = table.name

        sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
            table_name, columns)
        cur.copy_expert(sql=sql, file=s_buf)


def rapid_merge(client, ds_ref, table_name='comments', n_rows=30000, range=5):
    """
    Copy portions of a database num_rows long into another database. Resulting tables 
    can be UNION'd to create the final table equal to the initial table. 
    """
    for n in tqdm.tqdm(range):
        df = client.list_rows(table_name,
                              max_results=n_rows, 
                              start_index=n * n_rows).to_dataframe()

        df['score'] = df['text'].apply(sentiment_score)
        df.to_sql(f'table_{n:02}', engine, method=psql_insert_copy)
