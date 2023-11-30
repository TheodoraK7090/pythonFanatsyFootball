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
    
def query_sql(cursor, query):
    cursor.execute(query)
    return cursor

def add_new_player(cursor, playerdetails):
    name = playerdetails['player_name']
    age = playerdetails["age"]
    position = playerdetails['position']
    team_plays_on = playerdetails['team_plays_on']
    query = cursor.execute("INSERT INTO fantasy( player_name, age, position, team_plays_on" ") "
                           "VALUES(%s,%s,%s)", (name, age, position, team_plays_on))
the-sql-statement-python-mysql/
    return query_sql(cursor, query)

def check_if_player_exists(cursor, playerdetails):
    player_name = playerdetails['player_name']
    query = "SELECT * FROM fantasy WHERE player_name = \"%s\"" % player_name
    return query_sql(cursor, query)

def delete_player(cursor, playerdetails):
    player_name = playerdetails['player_name']
    query = "DELETE FROM fantasy WHERE player_name = \"%s\"" % player_name
    return query_sql(cursor, query)

def fetch_new_players():
    query = requests.get("http://espn-fantasy-football-api.s3-website.us-east-2.amazonaws.com/")
    datas = json.loads(query.text)
    return datas

def playerhunt( cursor):
    playerpage = fetch_new_players()
    add_or_delete_player( playerpage, cursor)

def add_or_delete_player( playerpage, cursor):
    for playerdetails in playerpage:
        check_if_player_exists(cursor, playerdetails)
        is_player_found = len(cursor.fetchall()) > 0
        if is_player_found:
            print("player is found: "+ playerdetails["player_name"] + " from " + playerdetails["team_plays_on"])
        else:
            print("New player is found: " + playerdetails["player_name"] + " from "+ playerdetails["team_plays_on"])
            add_new_player(cursor, playerdetails)

def main():
    conn = connect_to_sql()
    cursor = conn.cursor()
    create_tables(cursor)

if __name__ == '__main__':
    main()
