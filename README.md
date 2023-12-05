# pythonFanatsyFootball
Final Group Project for CNE 340, Fall 2023.
The group includes Theodora Kockel, Olakunle Abiola, and Nicholas McLendon.


README for NFL Football Game Predictions

# Overview

This Python script is designed to collect data from the Sportradar NFL API (v7) and store it in a MySQL database on a WAMP server for further analysis.You could also use a local database if you prefer. The collected data includes roster, and statistical information for all 32 teams in the NFL. The script is currently just analyzing data from the 2022 season, but can be adapted to data from a range of seasons including the current one. The script utilizes the "mysql.connector" library for database interactions and "requests" for making API calls.


# Before running the script, ensure the following: 

Install the requests and mysql-connector libraries. Everything else should come standard with Python 3.11. 

Set up a WAMP server with a MySQL database named fantasy_football_db.

Replace the placeholder API key in the api_key variable with a valid SportradarNFL API key. Instructions to obtain a free trial API key are below.

To obtain a SportradarNFL API Key visit https://developer.sportradar.com/member/register and fill out the required information fields. There is a student option for the “Industry” field. 

Once you are signed in, go to “My Account”, click on “Applications, and then click “Create a New App” You are NOT required to enter any credit card or payment information to obtain a trial key.

Fill out all of the information you can, you can leave the “Web Site” and “Register Callback URL” fields blank. Click on “Issue a new key for NFL Trial,” agree to the ToS and click “Register Application”. 

Next go back to “My Account" and click on “Keys”, then scroll down to NFL Trial and click “Get a Key for NFL Trial: Trial. 

You can now copy the displayed Key and use it for your API calls. Note that this trial key can only make one request per second, and only up to 1,000 requests per month. You may be temporarily unable to make API calls if you exceed these limits.

The API key does not disappear from this page, so you can always retrieve it from here if needed.


# API Documentation.

You can find the documentation for the sportradar API at https://developer.sportradar.com/docs/read/american_football/NFL_v7#nfl-api-overview.

We used these three endpoints to gather our data, but there are a lot more options available.

https://developer.sportradar.com/docs/read/american_football/NFL_v7#team-profile

https://developer.sportradar.com/docs/read/american_football/NFL_v7#team-roster

https://developer.sportradar.com/docs/read/american_football/NFL_v7#seasonal-statistics


# The calls are typically structured like this:

"https://api.sportradar.us/nfl/official/{access_level}/{version}/{language_code}/games/{year}/{nfl_season}/schedule.{format}?api_key={your_api_key}"

Replace {acess_level} with your level of access (either “trial” or “production”)

Replace {version} with what version of the API you want to use (“v7” was what I used, but I think the API is still supporting all the way back to “v4”)

Replace {language_code} with a 2 letter code for your desired language (“en” for english, “es” for Spanish, “it” for Italian, etc)

Replace {year} with a 4 digit year (YYYY) this API has data going back to the early 2000’s.

Replace {nfl_season with “PRE” to get preseason data for that year,  “REG” to get regular season information for that year, or  “PST” to get postseason information for that year.

Replace {format} with either “xml” or “json”. Whichever you prefer to work with.

Replace {your_api_key} with your NFL trial API key. (Or production API if applicable)

Please note: This goes over the basic structure for calling one of the API endpoints, but each endpoint may require minor tweaks to this formula. Be sure to consult the documentation for the correct structure of the specific endpoint you are trying to call upon.


# Code Structure
1. Database Connection
The script establishes a connection to the MySQL server using the connect_to_sql function.
2. Database Tables
The create_tables function creates three tables: teams, players, and team_statistics. These tables store team information, player details, and team statistics, respectively.
3. Data Insertion
insert_team_data: Inserts team data into the teams table, avoiding duplicates based on the team_id.
insert_team_statistics_data: Inserts team statistics into the team_statistics table, avoiding duplicates. It also updates existing records if they already exist.
insert_player_data: Inserts player data into the players table, avoiding duplicates based on the player_id.
4. API Calls
fetch_nfl_teams: Makes an API call to the Team Profile endpoint to get a list of NFL teams.
fetch_team_statistics: Makes an API call to the Seasonal Team Statistics endpoint to retrieve statistics for a specific team.
fetch_team_roster: Makes an API call to the Team Roster endpoint to fetch all of the player information for a specific team.
5. Query Functions
query_teams: Queries the teams table based on the team name.
query_team_statistics: Queries the team_statistics table based on the team name.
query_roster: Queries the players table to retrieve the entire roster for a team.
6. Prediction Function
predict_winner: Predicts the outcome of a match between two teams based on their statistics. Compares all of the collected statistics against each other for the two teams and assigns points for every key a team "wins" on. The team with the most points at the end of the comparison is declared the predicted winner.
7. Graph Generation Function:
generate_team_stats_graph: Generates a bar graph for a specific team's stats data.
generate_specific_stats_graph: Generates a bar graph of specific statistics for a team.
generate_comparison_stats_graph: Generates a graph comparing the stats of two teams against each other.
8. Main Function
The main function orchestrates the entire process. It fetches team data, team statistics, and player data, inserts them into the database, allows user input to predict the winner of a match, and displays the predicted winner.

# Usage

python script_name.py

When running the script just follow the on-screen instructions to input team names for predicting the winner. 


Please note: As of 12/3/2023 when entering the team names they must be spelled correctly and have their first letter capitalized. We’ll try to make the inputs a little less picky if we find the time.

# Potential Improvements

Error Handling: Enhance error handling to provide more informative messages in case of API errors or database issues.


Player Predictions: Consider re-implementing player predictions, as mentioned in the comments. This is going to be a lot of work, but it will make this script much more powerful for both real world, and fantasy predictions.


Interactive User Interface: Develop a more user-friendly interface for inputting team names, querying the database, and obtaining predictions.


API Key Handling: Securely manage API keys, potentially using environment variables, to avoid hardcoding in the script.


Optimization: Explore ways to optimize the script for faster execution, such as asynchronous API calls.
By addressing these improvements, the code can become more robust, maintainable, and user-friendly.
