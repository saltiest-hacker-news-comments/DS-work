from google.cloud import bigquery
from sqlalchemy import create_engine
from io import StringIO
import csv
import numpy as np
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "service_account_key_file.json"

client = bigquery.Client()
hn_dataset_ref = client.dataset('hacker_news', project='bigquery-public-data')
comment_ref = hn_dataset_ref.table('comments')
comments = client.get_table(comment_ref)


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


num_rows = 420000
engine = create_engine(
    'postgres://user:password@aws_rds_endpoint.amazonaws.com:5432/postgres')
for n in range(5):
    """Copy portions of a database num_rows long into another database. Resulting tables 
    can be UNION'd to create the final table equal to the initial table. """
    comment_df = client.list_rows(comments, max_results=num_rows, start_index=n *
                                  num_rows).to_dataframe()
    comment_df = comment_df.drop(
        columns=['deleted', 'dead', 'ranking', 'by', 'parent', 'time'])
    comment_df['salt_rank'] = np.random.ranf(size=len(comment_df))*2-1
    comment_df.to_sql(f'table_{n:02}', engine, method=psql_insert_copy)
