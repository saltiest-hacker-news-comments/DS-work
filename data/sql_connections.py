'''Includes the information and connections for connecting to PostgreSQL
database. ElephantSQL used initially, AWS set up for larger storage.'''
import psycopg2
from decouple import config


# Connection information
dbname = config('ESQL_R2_DBNAME')
user = config('ESQL_R2_USER')
password = config('ESQL_R2_PASSWORD')
host = config('ESQL_R2_HOST')

pg_conn = psycopg2.connect(dbname=dbname, user=user,
                           password=password, host=host)

pg_curs = pg_conn.cursor()

'''Create table for 'comments' table.
Columns match original Kaggle dataset'''
comments_table = """
                 CREATE TABLE IF NOT EXISTS comments (
                     id INTEGER,
                     by TEXT,
                     author TEXT,
                     time INTEGER,
                     time_ts TEXT,
                     text TEXT,
                     parent INTEGER,
                     deleted BOOLEAN,
                     dead BOOLEAN,
                     ranking INTEGER
                 );
                 """
pg_curs.execute(comments_table)

# Commit changes
pg_conn.commit()