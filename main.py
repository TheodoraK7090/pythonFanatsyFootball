# Theodora Kochel, Olakunle Abiola, and Nicholals McLendon
# CNE340 Fall 2023
# This code stores data from the sportsradar NFL API (v7) in a SQL database on a WAMP server for analysis.

import mysql.connector as sql
import time
import requests
import xml.dom.minidom

# Establish connection to SQL server and database
def connect_to_sql():
    conn = sql.connect(user='root', password='',
                                   host='127.0.0.1', database='fantasy_football_db')
    return conn

# Creates teams, players, and team_statistics tables if they don't already exist.
def create_tables(cursor):
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INT AUTO_INCREMENT PRIMARY KEY,
                team_id VARCHAR(100) UNIQUE,
                name TEXT,
                alias TEXT
            )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id VARCHAR(100) PRIMARY KEY,
            name TEXT,
            jersey_number INT,
            position TEXT,
            team_id VARCHAR(100),
            team_name TEXT,
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_statistics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            team_id VARCHAR(100),
            team_name TEXT,
            touchdowns FLOAT,
            rushing_avg_yards FLOAT,
            rushing_attempts FLOAT,
            receiving_avg_yards FLOAT,
            receiving_targets FLOAT,
            pass_cmp_pct FLOAT,
            pass_interceptions FLOAT,
            pass_sack_yards FLOAT,
            pass_touchdowns FLOAT,
            field_goals_pct FLOAT,
            tloss FLOAT,
            sacks FLOAT,
            interceptions FLOAT,
            qb_hits FLOAT,
            three_and_outs_forced FLOAT,
            fourth_down_stops FLOAT
        )
    ''')


# Inserts teams data into their table, avoids duplicates
def insert_team_data(cursor, team_id, name, alias):
    try:
        cursor.execute('''
            INSERT INTO teams (team_id, name, alias) VALUES (%s, %s, %s)
        ''', (team_id, name, alias))
    except sql.IntegrityError:
        # Ignore if team_id already exists (duplicate)
        pass

# Inserts team statistics data into their table, avoids duplicates.
def insert_team_statistics_data(cursor, team_id, team_name, team_statistics_dom):
    try:
        touchdowns = float(team_statistics_dom.getElementsByTagName('touchdowns')[0].getAttribute('total'))
        rushing_avg_yards = float(team_statistics_dom.getElementsByTagName('rushing')[0].getAttribute('avg_yards'))
        rushing_attempts = float(team_statistics_dom.getElementsByTagName('rushing')[0].getAttribute('attempts'))
        receiving_avg_yards = float(team_statistics_dom.getElementsByTagName('receiving')[0].getAttribute('avg_yards'))
        receiving_targets = float(team_statistics_dom.getElementsByTagName('receiving')[0].getAttribute('targets'))
        pass_cmp_pct = float(team_statistics_dom.getElementsByTagName('passing')[0].getAttribute('cmp_pct'))
        pass_interceptions = float(team_statistics_dom.getElementsByTagName('passing')[0].getAttribute('interceptions'))
        pass_sack_yards = float(team_statistics_dom.getElementsByTagName('passing')[0].getAttribute('sack_yards'))
        pass_touchdowns = float(team_statistics_dom.getElementsByTagName('passing')[0].getAttribute('touchdowns'))
        field_goals_pct = float(team_statistics_dom.getElementsByTagName('field_goals')[0].getAttribute('pct'))
        tloss = float(team_statistics_dom.getElementsByTagName('defense')[0].getAttribute('tloss'))
        sacks = float(team_statistics_dom.getElementsByTagName('defense')[0].getAttribute('sacks'))
        interceptions = float(team_statistics_dom.getElementsByTagName('defense')[0].getAttribute('interceptions'))
        qb_hits = float(team_statistics_dom.getElementsByTagName('defense')[0].getAttribute('qb_hits'))
        three_and_outs_forced = float(team_statistics_dom.getElementsByTagName('defense')[0].getAttribute('three_and_outs_forced'))
        fourth_down_stops = float(team_statistics_dom.getElementsByTagName('defense')[0].getAttribute('fourth_down_stops'))

        # Check if the record already exists
        cursor.execute('SELECT * FROM team_statistics WHERE team_id = %s', (team_id,))
        existing_record = cursor.fetchone()

        if existing_record:
            # Update the existing record
            cursor.execute('''
                        UPDATE team_statistics SET
                        team_name = %s,
                        touchdowns = %s,
                        rushing_avg_yards = %s,
                        rushing_attempts = %s,
                        receiving_avg_yards = %s,
                        receiving_targets = %s,
                        pass_cmp_pct = %s,
                        pass_interceptions = %s,
                        pass_sack_yards = %s,
                        pass_touchdowns = %s,
                        field_goals_pct = %s,
                        tloss = %s,
                        sacks = %s,
                        interceptions = %s,
                        qb_hits = %s,
                        three_and_outs_forced = %s,
                        fourth_down_stops = %s
                        WHERE team_id = %s
                    ''', (
                team_name, touchdowns, rushing_avg_yards, rushing_attempts,
                receiving_avg_yards, receiving_targets, pass_cmp_pct, pass_interceptions,
                pass_sack_yards, pass_touchdowns, field_goals_pct, tloss, sacks,
                interceptions, qb_hits, three_and_outs_forced, fourth_down_stops,
                team_id
            ))
        else:
            # Insert a new record
            cursor.execute('''
                        INSERT INTO team_statistics (
                            team_id, team_name, touchdowns, rushing_avg_yards, rushing_attempts,
                            receiving_avg_yards, receiving_targets, pass_cmp_pct, pass_interceptions,
                            pass_sack_yards, pass_touchdowns, field_goals_pct, tloss, sacks,
                            interceptions, qb_hits, three_and_outs_forced, fourth_down_stops
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                team_id, team_name, touchdowns, rushing_avg_yards, rushing_attempts,
                receiving_avg_yards, receiving_targets, pass_cmp_pct, pass_interceptions,
                pass_sack_yards, pass_touchdowns, field_goals_pct, tloss, sacks,
                interceptions, qb_hits, three_and_outs_forced, fourth_down_stops
            ))

    except Exception as e:
        print(f"Error inserting team statistics for team_id {team_id}: {e}")

# Inserts player data into their table, we were originally going to use this data to make predictions, but that ended up being a lot more trouble to code then just using overall team stats. Left code in just because.
def insert_player_data(cursor, player_id, name, jersey_number, position, team_id, team_name):
    try:
        cursor.execute('''
            INSERT INTO players (id, name, jersey_number, position, team_id, team_name) VALUES (%s, %s, %s, %s, %s, %s)
        ''', (player_id, name, jersey_number, position, team_id, team_name))
    except sql.IntegrityError:
        # Ignore if player_id already exists (duplicate)
        pass

# Api call to Team Profile endpoint
def fetch_nfl_teams(api_key):
    # Set endpoint and get response
    url = "https://api.sportradar.us/nfl/official/trial/v7/en/league/hierarchy.xml?apikey={}".format(api_key)
    response = requests.get(url, params={"api_key": api_key})

    # Make sure the response code is good
    if response.status_code == 200:
        # Convert the response into something more human-readable. Made it much easier to work with.
        dom = xml.dom.minidom.parseString(response.text)
        # Identify team elements so we can use their data.
        teams = dom.getElementsByTagNameNS("http://feed.elasticstats.com/schema/football/nfl/hierarchy-v7.0.xsd", "team")
        return teams
    else:
        print(f"Error: {response.status_code}")
        return []

# Api call to Seasonal Team Statistics endpoint
def fetch_team_statistics(api_key, team_id):
    # Set endpoint and get response
    url = "http://api.sportradar.us/nfl/official/trial/v7/en/seasons/2022/REG/teams/{}/statistics.xml?api_key={}".format(str(team_id), api_key)
    response = requests.get(url)

    # Make sure the response code is good
    if response.status_code == 200:
        # Convert the response into something more human-readable. Made it much easier to work with.
        team_statistics = xml.dom.minidom.parseString(response.text)
        return team_statistics
    else:
        print(f"Error fetching team statistics for team_id {team_id}: {response.status_code}")
        return None

# API call to Team Roster endpoint, we were originally going to use player data to make predictions, this was so I could find their unique player_id to use with the Player Profile and Seasonal Statistics endpoints. Left code in just because.
def fetch_team_roster(api_key, team_id):
    url = "https://api.sportradar.us/nfl/official/trial/v7/en/teams/{}/full_roster.json?api_key={}".format(str(team_id), api_key)
    response = requests.get(url)

    if response.status_code == 200:
        roster_data = response.json()
        return roster_data.get('players', [])
    else:
        print(f"Error fetching roster for team_id {team_id}: {response.status_code}")
        return []

# Function for querying the teams table
def query_teams(cursor, team_name):
    select_query = "SELECT * FROM teams WHERE name = %s"
    cursor.execute(select_query, (team_name,))
    rows = cursor.fetchall()
    for row in rows:
        print(row)

# Function for querying the team_statistics table.
def query_team_statistics(cursor, team_name):
    select_team_statistics_query = "SELECT * FROM team_statistics WHERE team_name = %s"
    cursor.execute(select_team_statistics_query, (team_name,))
    rows = cursor.fetchall()

    if not rows:
        # Return an empty dictionary if no statistics found.
        return {}

    # Retrieves the column names from the result set's description
    column_names = [description[0] for description in cursor.description]
    # Creates a dictionary that pairs column names and their values, starting from the third column to skip the Primary Key and the team_id
    team_stats = dict(zip(column_names[2:], rows[0][2:]))

    print(team_stats)

    return team_stats

# Function for querying the players table in a way that pulls the whole roster for a team.
def query_roster(cursor, team_name):
    select_roster_query = "SELECT * FROM players WHERE team_name = %s"
    cursor.execute(select_roster_query, (team_name,))
    rows = cursor.fetchall()
    print(f"Roster for Team {team_name}:")
    for row in rows:
        print(row)

# Function for predicting the outcome of a match between two teams.
def predict_winner(cursor, team1_name, team2_name):
    # Use query_team_statistics function to get team statistics
    team1_stats = query_team_statistics(cursor, team1_name)
    team2_stats = query_team_statistics(cursor, team2_name)

    # Initialize scores for each team as zero.
    team1_score = 0
    team2_score = 0

    # Compare values for each key in the dictionaries and update scores
    for key in team1_stats:
        team1_value = team1_stats[key]
        team2_value = team2_stats[key]

        if team1_value > team2_value:
            team1_score += 1
        elif team1_value < team2_value:
            team2_score += 1
        else:
            pass

    print(f"{team1_name} score: {team1_score}")
    print(f"{team2_name} score: {team2_score}")

    # Determine the winner based on the scores
    if team1_score > team2_score:
        return team1_name
    elif team1_score < team2_score:
        return team2_name
    else:
        return "It's a tie"

def main():
    # Set api key for use
    api_key = "hzypnutkwajpqcpssmu4zaat"  # Replace with your own API key if you plan on running this project after the quarter is over as this one is temporary. You can ask Nick or refer to the documentation for guidance.

    # Create connection and cursor variables
    conn = connect_to_sql()
    cursor = conn.cursor()
    create_tables(cursor)

    # Create variable to iterate through the teams data with
    nfl_teams = fetch_nfl_teams(api_key)

    # Iterate through teams and insert data into the teams table.
    for team in nfl_teams:
        time.sleep(2) # API will only take one request a second, this program generates a couple dozen while it runs. They were running faster than one a second so I would get 403 errors randomly that would leave holes in the tables/data. The sleep timer prevents this, but causes the program to take a couple minutes to finish running.
        team_id = team.getAttribute("id")
        name = team.getAttribute("name")
        alias = team.getAttribute("alias")
        insert_team_data(cursor, team_id, name, alias)

    conn.commit()

    # Fetch teams from the teams table
    select_teams_query = "SELECT team_id, name FROM teams"
    cursor.execute(select_teams_query)
    teams = cursor.fetchall()

    # Iterate through teams and insert their statistics into the team_statistics table.
    for team in teams:
        time.sleep(2) # API will only take one request a second, this program generates a couple dozen while it runs. They were running faster than one a second so I would get 403 errors randomly that would leave holes in the tables/data. The sleep timer prevents this, but causes the program to take a couple minutes to finish running.
        team_id, team_name = team

        # Fetch team statistics
        team_statistics = fetch_team_statistics(api_key, team_id)

        # Insert team statistics into the "team_statistics" table
        insert_team_statistics_data(cursor, team_id, team_name, team_statistics)

        # Fetch team roster
        time.sleep(2) # API will only take one request a second, this program generates a couple dozen while it runs. They were running faster than one a second so I would get 403 errors randomly that would leave holes in the tables/data. The sleep timer prevents this, but causes the program to take a couple minutes to finish running.
        team_roster = fetch_team_roster(api_key, team_id)

        # Insert player data into the players table
        for player in team_roster:
            player_id = player.get('id')
            name = player.get('name')
            jersey_number = player.get('jersey')
            position = player.get('position')

            insert_player_data(cursor, player_id, name, jersey_number, position, team_id, team_name)

    conn.commit()

    # Input commands allow you to match two teams against each other. Their names must be spelled correctly with the first letter capitialized for this to work. We can try to improve this if we get time.
    team1_name_input = input("Enter the name of team 1: ")
    team2_name_input = input("Enter the name of team 2: ")

    # Predict the winner of the game.
    winner_prediction = predict_winner(cursor, team1_name_input, team2_name_input)
    print(f"The predicted winner is: {winner_prediction}")

    conn.close()

if __name__ == '__main__':
    main()

# The code below was used while I was troubleshooting the predict_winner function after the data was already collected. I left it in just in case.

    #conn = connect_to_sql()
    #cursor = conn.cursor()

    #team1_name_input = input("Enter the name of team 1: ")
    #team2_name_input = input("Enter the name of team 2: ")

    #winner_prediction = predict_winner(cursor, team1_name_input, team2_name_input)
    #print(f"The predicted winner is: {winner_prediction}")

    #query_teams(cursor, input("Please enter a team name"))
    #query_team_statistics(cursor, input("Please enter a team name"))
    #query_roster(cursor, input("Please enter a team name"))