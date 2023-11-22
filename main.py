#Theodora Kochel
#CNE340 Fall 11/21/23
#This code is setting up a database for creating a Fantasy Football team.  This will go into a WAMP server.
#Nicholas McLendon and Olakunle Abiola are also partners in this project.

import mysql.connector
import time
import json
import requests
from datetime import datetime
import html2text


def connect_to_sql():
    conn = mysql.connector.connect(user='root', password='',
                                   host='127.0.0.1', database='')
    return conn


def create_tables(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS fantasy_football (id INT PRIMARY KEY auto_increment, player_name Text, 
    age INT, position TEXT, team_plays_on TEXT; ''')

