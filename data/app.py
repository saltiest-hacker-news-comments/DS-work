# Use python decouple to store env
import pandas as pd
import numpy as np
import json
import psycopg2
from flask import Flask, json, jsonify, request, send_file
from decouple import config


APP = Flask(__name__)

