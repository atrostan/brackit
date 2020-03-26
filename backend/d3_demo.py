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
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

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

print(pd.read_sql_query('select * from tournament', cnx))
print(pd.read_sql_query('select * from match', cnx))
def handle_progression(tournament, tkn):
    """Mimic Progression Handling of a Tournament
    
    Arguments:
        tournament {TournamentModel} -- a sqlAlchemy db model represnting
        a double elimination bracket tournament
        tkn {string} -- a unique authentication token
        used to ensure that only the tournament organizer enters scores in a 
        bracket 
    """
    for bracket in tournament.brackets:
        for round in bracket.rounds:
            for match in round.matches:

                url = \
                    f'{URL_PREFIX}api/match/{match.id}/report-match'
                score = np.random.randint(2, 6)
                payload = json.dumps({
                    "entrant1_score": score,
                    "entrant2_score": score-2,
                    "winner": match.user_1,
                    "loser": match.user_2
                })
                r = requests.post(
                    url, data=payload, headers=headers, 
                    auth=(tkn, 'unused')
                )

                # print(match.id)
                # if match.id == 8:
                #     urlgf = \
                #         f'{URL_PREFIX}api/match/{match.id}/report-match'
                #     payloadgf = json.dumps({
                #         "entrant1_score": 0,
                #         "entrant2_score": 3,
                #         "winner": match.user_2,
                #         "loser": match.user_1
                #     })
                # elif match.id == 9:
                #     urlgfr = \
                #         f'{URL_PREFIX}api/match/{match.id}/report-match'
                #     payloadgfr = json.dumps({
                #         "entrant1_score": 3,
                #         "entrant2_score": 0,
                #         "winner": match.user_1,
                #         "loser": match.user_2
                #     })
                # else:
                #     url = \
                #         f'{URL_PREFIX}api/match/{match.id}/report-match'
                #     payload = json.dumps({
                #         "entrant1_score": 2,
                #         "entrant2_score": 0,
                #         "winner": match.user_1,
                #         "loser": match.user_2
                #     })
                #     r = requests.post(
                #         url, data=payload, headers=headers, 
                #         auth=(tkn, 'unused')
                #     )
                print(json.loads(r.content))
    # requests.post(urlgf, data=payloadgf, headers=headers, auth=(tkn, 'unused'))
    # requests.post(urlgfr, data=payloadgfr, headers=headers, auth=(tkn, 'unused'))


def create_tournament(tournament_name):
    # get miguel's token
    url = f'{URL_PREFIX}api/token'
    r = requests.get(url, auth=('miguel', 'python'))
    tkn = json.loads(r.content)['token']

    # miguel creates lobby
    url = f'{URL_PREFIX}api/create/lobby/'
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    payload = json.dumps({
        "tournament_name" : tournament_name
    })
    r = requests.post(url, data=payload, headers=headers, auth=(tkn, 'unused'))

    print(json.loads(r.content))
    lobby_id = json.loads(r.content)['lobby_id']
    # miguel adds users to his lobby

    q = """select * from user where role == 'User' """

    # posted a user
    df = pd.read_sql_query(q, cnx)

    users = df.head(7).username.values
    np.random.shuffle(users)
    print(len(users))

    url = f'{URL_PREFIX}api/lobby/{lobby_id}/add-user/'
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

    url = f'{URL_PREFIX}api/lobby/{lobby_id}/add-user/'
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

    payload = json.dumps({
        "username" : f"guest.{tournament_name.split('.')[-1]}",
        "role" : "Guest",
        "seed" : 10
    })
    r = requests.post(url, data=payload, headers=headers, auth=(tkn, 'unused'))
    print(json.loads(r.content))

    # create a tournament from lobby 
    url = f'{URL_PREFIX}api/lobby/{lobby_id}/create-tournament/'
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    payload = json.dumps({})
    r = requests.post(url, payload, headers=headers, auth=(tkn, 'unused'))

    tid = json.loads(r.content)['tournament_id']

    tournament = TournamentModel.query.filter_by(id=int(tid)).first_or_404()

    # print(len(tournament.brackets.rounds.matches))
    print(f'handling progression for tournament {tid}')

    # get miguel's token / log miguel in
    url = f'{URL_PREFIX}api/token'
    r = requests.get(url, auth=('miguel', 'python'))
    tkn = json.loads(r.content)['token']
    print(pd.read_sql_query('select * from match', cnx))

    # TO (miguel) can enter scores
    handle_progression(tournament, tkn)



url = f'{URL_PREFIX}api/users'

# post miguel
payload = json.dumps({
    "username":"miguel",
    "password":"python",
    "email":"miguel@gmail.com"
})

r = requests.post(url, data=payload, headers=headers)
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


[create_tournament(f'miguel.tourney.{i}') for i in range(1)]

# print(pd.read_sql_query('select * from tournament', cnx))
# print(pd.read_sql_query('select * from match', cnx))


mid = UserModel.query.filter_by(username='miguel').first().id
# show miguel's wins and losses:
url = f'{URL_PREFIX}api/user/{mid}/winsandlosses'

r = requests.get(url, headers=headers)
print(json.loads(r.content))

