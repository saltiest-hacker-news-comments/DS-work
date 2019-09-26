"""Main application for Salty HN app
"""
import pandas as pd
import numpy as np
from decouple import config
from flask import Flask, json, jsonify, request, send_file, render_template
import psycopg2


# Elephant DB connection info
dbname = config('ESQL_R2_DBNAME')
user = config('ESQL_R2_USER')
password = config('ESQL_R2_PASSWORD')
host = config('ESQL_R2_HOST')


def create_app():
    """Create and config routes"""
    app = Flask(__name__)
#    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['ENV'] = 'debug'  # TODO change before heroku deployment
#    DB.init_app(app)

    def saltiest_comments():
        """Query to get the text of the most salty comments.
        Returns a list of (comment, score) tuples. """
        pg_conn = psycopg2.connect(dbname=dbname, user=user,
                                   password=password, host=host)
        pg_curs = pg_conn.cursor()
        salty_comment_query = """SELECT text, score
                                FROM salt
                                ORDER BY score asc
                                LIMIT 100;"""
        pg_curs.execute(salty_comment_query)
        results = pg_curs.fetchall()
        pg_curs.close()
        pg_conn.close()
        return results

    def saltiest_users():
        """Query to get the names of the most salty users.
        Returns a list of (user, score) tuples. """
        pg_conn = psycopg2.connect(dbname=dbname, user=user,
                                   password=password, host=host)
        pg_curs = pg_conn.cursor()
        salty_user_query = """SELECT author, SUM(score) AS total_score
                                FROM salt
                                GROUP BY author
                                ORDER BY total_score ASC
                                LIMIT 100;"""
        pg_curs.execute(salty_user_query)
        results = pg_curs.fetchall()
        pg_curs.close()
        pg_conn.close()
        return results

    def saltiest_hours():
        """Query to get the hours of the day  most salty users.
        Returns a list of (hour, comment count) tuples. """
        pg_conn = psycopg2.connect(dbname=dbname, user=user,
                                   password=password, host=host)
        pg_curs = pg_conn.cursor()
        salty_hours_query = """SELECT EXTRACT(HOUR FROM time_ts) AS hour, COUNT(*)
                                FROM salt
                                WHERE score < -1.0
                                GROUP BY hour
                                ORDER BY hour ASC;"""
        pg_curs.execute(salty_hours_query)
        results = pg_curs.fetchall()
        pg_curs.close()
        pg_conn.close()
        return results

    def saltiest_days():
        """Query to get the day of the week and the count of comments scoring less than -1.
        Returns a list of (day, comment count) tuples. """
        pg_conn = psycopg2.connect(dbname=dbname, user=user,
                                   password=password, host=host)
        pg_curs = pg_conn.cursor()
        salty_days_query = """SELECT EXTRACT(ISODOW FROM time_ts) AS day, COUNT(*)
                                FROM salt
                                WHERE score < -1.0       
                                GROUP BY day
                                ORDER BY day ASC;"""
        pg_curs.execute(salty_days_query)
        results = pg_curs.fetchall()
        pg_curs.close()
        pg_conn.close()
        return results

    def user_comments(name="pg"):
        """Query to get the text of a particular user and their salt scores.
        Returns a list of (comment, score) tuples. """
        pg_conn = psycopg2.connect(dbname=dbname, user=user,
                                   password=password, host=host)
        pg_curs = pg_conn.cursor()
        salty_days_query = """SELECT text , score
                                FROM salt
                                WHERE author = '""" + name + """'
                                ORDER BY score
                                LIMIT 10;"""
        pg_curs.execute(salty_days_query)
        results = pg_curs.fetchall()
        pg_curs.close()
        pg_conn.close()
        return results

    @app.route("/")
    def root():
        return render_template('base.html', title="A Salty Flask")

    @app.route("/salty-users")
    def user_list():
        results = saltiest_users()
        # return render_template('salty-table.html', title='Saltiest Users', results=results)
        return jsonify(dict(results))

    @app.route("/salty-comments")
    def comment_list():
        results = saltiest_comments()
        return jsonify(dict(results))

    @app.route("/salty-hours")
    def hours_list():
        results = saltiest_hours()
        return jsonify(dict(results))

    @app.route("/salty-days")
    def days_list():
        results = saltiest_days()
        return jsonify(dict(results))

    @app.route("/user-comments/<name>", methods=['GET'])
    def user_comments_list(name):
        results = user_comments(name)
        return jsonify(dict(results))

    return app
