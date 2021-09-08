import requests
import json


class FPL_Engine:
    def __init__(self, credentials):
        self.credentials = credentials

    def get_fixtures(self):
        url = self.credentials["fixtures_url"]
        r = requests.get(url)
        json = r.json()
        return json

    def get_teams(self):
        url = self.credentials["teams_url"]
        r = requests.get(url)
        json = r.json()
        teams = json['teams']
        return teams

    def get_players(self):
        url = self.credentials["players_url"]
        r = requests.get(url)
        json = r.json()
        players = json['elements']
        return players

    def get_detailed_player_info(self, player_id):
        url = f'https://fantasy.premierleague.com/api/element-summary/{player_id}/'
        r = requests.get(url)
        json = r.json()
        history = json['history']
        future = json['fixtures']
        return history, future

    def manager_fpl_data(self):
        url = self.credentials["login_url"]
        pwd = self.credentials["password"]
        email = self.credentials["email"]
        redirect_uri = self.credentials["redirect_uri"]
        app_name = self.credentials["app_name"]
        payload = {
            'password': pwd,
            'login': email,
            'redirect_uri': redirect_uri,
            'app': app_name
        }
        session = requests.session()
        session.post(url, data=payload)
        my_team_url = self.credentials["my_team_url"] + self.credentials["manager_id"] + '/'
        response = session.get(my_team_url)
        json = response.json()
        return json


