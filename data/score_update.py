import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from google.cloud import bigquery
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from decouple import config


# Establish connection to database
engine = create_engine('postgres://<user>:<password>@<host>:5432/<dbname>')

# Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config('GOOGLE_APPLICATION_CREDENTIALS')

# Open bigquery client connection
client = bigquery.Client()

# Create bigquery dataset reference
hn_ref = client.dataset('hacker_news', project='bigquery-public-data')

def sentiment_score(comment):
    """
    From Machine Learning Engineer
    """
    analyser = SentimentIntensityAnalyzer()
    
    x = 0
    score = analyser.polarity_scores(comment)
    x = x + score['pos']
    x = x + score['compound']
    x = x - score['neg'] 
    
    return x

def df_create(client, ds_ref, table_name='comments', count=30000):
    """
    Create a pandas dataframe from Google bigquery connection
    of comments table.

    Add sentiment analysis score column
    
    Parameters
    ---------------------------------------------------------
    client:       bigquery connection
    ds_ref:       a connected bigquery dataset reference
    table_name:   (str) name of the table
    count:        (int) the number of rows from the table to return
    
    Output
    ---------------------------------------------------------
    Returns a pandas dataframe
    """
    table_ref = ds_ref.table(table_name)
    table = client.get_table(table_ref)
    
    df = client.list_rows(table, max_results=count).to_dataframe
    df['score'] = df['text'].apply(sentiment_score)
    
    return df

def to_postgres(df, title, engine):
    """
    Migrate pandas dataframe to postgresql database.
    
    Only works with SQLAlchemy or sqlite.
    
    For reference:
    https://pandas.pydata.org/pandas-docs/version/0.23.4/generated/pandas.DataFrame.to_sql.html
    
    
    Parameters
    ---------------------------------------------------------
    df: a pandas dataframe
    title (str): what you want to call the SQL table
    engine: the sql engine/connection you established
    
    Output
    ---------------------------------------------------------
    Returns nothing. Check to see if you can query the 
    database using SQLAlchemy in python.
    """
    df.to_sql(title, engine, index=False)