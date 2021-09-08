import requests
import json
from collections import defaultdict

class FPL_Engine:
    def __init__(self, credentials):
        self.credentials = credentials
        self.teams = self.get_teams()
        self.fixtures = self.get_fixtures()
        self.players = self.get_players()
        self.my_data = self.manager_fpl_data()
        self.data = {}
        self.element_types = self.get_element_types()
        self.starting_lineup, self.bench = self.build_team()

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
        self.teams = teams
        return teams

    def get_players(self):
        url = self.credentials["players_url"]
        r = requests.get(url)
        json = r.json()
        players = json['elements']
        players_refactor = {}
        for card in players:
            players_refactor[card['id']] = {i:card[i] for i in card if i!='id'}

        return players_refactor


        return players

    def get_element_types(self):
        url = self.credentials["players_url"]
        r = requests.get(url)
        json = r.json()
        types = json['element_types']
        types_refactor = {}
        for card in types:
            types_refactor[card['id']] = {i:card[i] for i in card if i!='id'}
        return types_refactor

    def get_detailed_player_info(self, player_id):
        url = f'https://fantasy.premierleague.com/api/element-summary/{player_id}/'
        r = requests.get(url)
        json = r.json()
        history = json['history']
        future = json['fixtures']
        return history, future

    def manager_fpl_data(self):
        url = self.credentials["login_url"]
        pwd = self.credentials["fantasy_pwd"]
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

    def build_team(self):
        starting_lineup = []
        bench = []
        for card in self.my_data['picks']:
            element = card['element']
            player = self.players[element]
            position = player['element_type']
            position_str = self.element_types[position]['singular_name_short']
            first_name = player['first_name']
            last_name = player['second_name']

            if card['position'] < 12:
                starting_lineup.append([first_name, last_name, position_str])
            else:
                bench.append([first_name, last_name, position_str])

        return starting_lineup, bench

    def display_team(self):
        team = {"GKP":" ", "DEF":" ", "MID":" ", "FWD":" "}
        for player in self.starting_lineup:
            team[player[2]] += "-".join(player) + "  "
        print(team["GKP"].center(120), '\n\n')
        print(team["DEF"].center(120), '\n\n')
        print(team["MID"].center(120), '\n\n')
        print(team["FWD"].center(120))






