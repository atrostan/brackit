from app import db
import numpy as np

from app.models import Tournament as TournamentModel
from app.models import Bracket as BracketModel
from app.models import Match as MatchModel
from app.models import Round as RoundModel
from app.models import User as UserModel
from app.models import Lobby as LobbyModel
from app.models import LobbySeed as LobbySeedModel

from tournament import Tournament

import numpy as np

from sqlalchemy.sql.expression import func, select

from tournament import (
    BracketTypes,
    Tournament,
    Match
)
import sqlite3
import pandas as pd
import uuid
import requests
import json
import random


URL_PREFIX = 'http://127.0.0.1:5000/'

def handle_progression(tournament, tkn):
    """Mimic Progression Handling of a Tournament
    
    Arguments:
        tournament {TournamentMode} -- a sqlAlchemy db model represnting
        a double elimination bracket tournament
        tkn {string} -- a unique authentication token
        used to ensure that only the tournament organizer enters scores in a 
        bracket 
    """
    
    for bracket in tournament.brackets:
        for round in bracket.rounds:
            for match in round.matches:
                print(match.id)
                if match.id == 8:
                    urlgf = \
                        f'{URL_PREFIX}api/match/{match.id}/report-match'
                    payloadgf = json.dumps({
                        "entrant1_score": 0,
                        "entrant2_score": 3,
                        "winner": match.user_2,
                        "loser": match.user_1
                    })
                elif match.id == 9:
                    urlgfr = \
                        f'{URL_PREFIX}api/match/{match.id}/report-match'
                    payloadgfr = json.dumps({
                        "entrant1_score": 3,
                        "entrant2_score": 0,
                        "winner": match.user_1,
                        "loser": match.user_2
                    })
                else:
                    url = \
                        f'{URL_PREFIX}api/match/{match.id}/report-match'
                    payload = json.dumps({
                        "entrant1_score": 2,
                        "entrant2_score": 0,
                        "winner": match.user_1,
                        "loser": match.user_2
                    })
                    r = requests.post(
                        url, data=payload, headers=headers, 
                        auth=(tkn, 'unused')
                    )
                print(json.loads(r.content))
    requests.post(urlgf, data=payloadgf, headers=headers, auth=(tkn, 'unused'))
    requests.post(urlgfr, data=payloadgfr, headers=headers, auth=(tkn, 'unused'))


# purge all tables first

Models = [
    BracketModel, 
    LobbyModel,
    TournamentModel, 
    MatchModel, 
    RoundModel, 
    UserModel, 
    LobbySeedModel
]

cnx = sqlite3.connect(r'./app.db')
db.session.close()
def purge(Model):
    [db.session.delete(row) for row in Model.query.all()]

# purge all tables first

[purge(Model) for Model in Models]
db.session.commit()

url = f'{URL_PREFIX}api/users'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

# post miguel
payload = json.dumps({
    "username":"miguel",
    "password":"python",
    "email":"miguel@gmail.com"
})

r = requests.post(url, data=payload, headers=headers)

url = f'{URL_PREFIX}api/users'
# post the rest of the users
users = [
    ('TPN', 'TPN@example.com'),
    ('AngryFalco', 'AngryFalco@example.com'),
    ('Sunrisebanana', 'Sunrisebanana@example.com'),
    ('Ptolemy', 'Ptolemy@example.com'),
    ('Vik', 'Vik@example.com'),
    ('Kevin', 'Kevin@example.com'),
    ('Spaceghost', 'Spaceghost@example.com'),
    ('Burnaby', 'Burnaby@example.com'),
]

for username, email in users:
    payload = json.dumps({
        "username":username,
        "password":username.lower(),
        "email":email.lower()
    })

    r = requests.post(url, data=payload, headers=headers)

# get miguel's token
url = f'{URL_PREFIX}api/token'
r = requests.get(url, auth=('miguel', 'python'))
tkn = json.loads(r.content)['token']

# miguel creates lobby
url = f'{URL_PREFIX}api/create/lobby/'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
payload = json.dumps({
    "tournament_name" : "miguel's tourneys"
})
r = requests.post(url, data=payload, headers=headers, auth=(tkn, 'unused'))

# miguel adds users to his lobby

q = 'select * from user'

# posted a user
df = pd.read_sql_query(q, cnx)

users = df.username.values
np.random.shuffle(users)

url = f'{URL_PREFIX}api/lobby/1/add-user/'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

seeds = random.sample(range(1, len(users)+1), len(users)) 
roles = ["User" for u in users]
for u, s, r in zip(users, roles, seeds):
    print(f'adding {u}, {s}, {r}')
    payload = json.dumps({
        "username" : u,
        "role" : s,
        "seed" : r
    })
    r = requests.post(url, data=payload, headers=headers, auth=(tkn, 'unused'))
    print(json.loads(r.content))

# miguel adds a guest user

url = f'{URL_PREFIX}api/lobby/1/add-user/'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

payload = json.dumps({
    "username" : "guestb",
    "role" : "Guest",
    "seed" : 10
})
r = requests.post(url, data=payload, headers=headers, auth=(tkn, 'unused'))
print(json.loads(r.content))

# TPN tries to add his own guests to miguel's lobby
url = f'{URL_PREFIX}api/lobby/1/add-user/'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

payload = json.dumps({
    "username" : "guestx",
    "role" : "Guest",
    "seed" : 1
})
r = requests.post(url, data=payload, headers=headers, auth=('TPN', 'tpn'))
print(json.loads(r.content))

url = 'http://127.0.0.1:5000/api/lobby/1/entrants'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
# payload = json.dumps({
#     "username" : "AngryFalco",
#     "role" : "User"
# })
r = requests.get(url, headers=headers,)
content =  json.loads(r.content)
print(content)

# create a tournament from lobby 1
url = 'http://127.0.0.1:5000/api/lobby/1/create-tournament/'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
payload = json.dumps({})
r = requests.post(url, payload, headers=headers, auth=(tkn, 'unused'))

print(json.loads(r.content))

q = 'select * from tournament'

# posted a user
df = pd.read_sql_query(q, cnx)
tid = df.head(1)['id'].values[0]
print(tid)
tournament = TournamentModel.query.filter_by(id=int(tid)).first_or_404()

# TO (miguel) can enter scores
# handle_progression(tournament, tkn)

# get TPN's token / log TPN in
url = f'{URL_PREFIX}api/token'
r = requests.get(url, auth=('TPN', 'tpn'))
c_tkn = json.loads(r.content)['token']

# TPN can't enter scores
handle_progression(tournament, c_tkn)

# get miguel's token / log miguel in
url = f'{URL_PREFIX}api/token'
r = requests.get(url, auth=('miguel', 'python'))
tkn = json.loads(r.content)['token']

# TO (miguel) can enter scores
handle_progression(tournament, tkn)

# print all the tables for good measure

