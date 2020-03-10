from app import db
import numpy as np

from app.models import Tournament as TournamentModel
from app.models import Bracket as BracketModel
from app.models import Match as MatchModel
from app.models import Round as RoundModel
from app.models import User as UserModel

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

def handle_progression(tournament, tkn):
    """Mimic Progression Handling of a Tournament
    
    Arguments:
        tournament {TournamentMode} -- a sqlAlchemy db model represnting
        a double elimination bracket tournament
        tkn {string} -- a unique authentication token
        used to ensure that only the tournament organizer enters scores in a 
        bracket 
    """
    url_prefix = 'http://127.0.0.1:5000/'
    for bracket in tournament.brackets:
        for round in bracket.rounds:
            for match in round.matches:
                if match.id == 8:
                    urlgf = \
                        f'{url_prefix}api/match/{match.id}/report-match'
                    payloadgf = json.dumps({
                        "entrant1_score": 0,
                        "entrant2_score": 3,
                        "winner": match.user_2,
                        "loser": match.user_1
                    })
                elif match.id == 9:
                    urlgfr = \
                        f'{url_prefix}api/match/{match.id}/report-match'
                    payloadgfr = json.dumps({
                        "entrant1_score": 3,
                        "entrant2_score": 0,
                        "winner": match.user_1,
                        "loser": match.user_2
                    })
                else:
                    url = \
                        f'{url_prefix}api/match/{match.id}/report-match'
                    payload = json.dumps({
                        "entrant1_score": 2,
                        "entrant2_score": 0,
                        "winner": match.user_1,
                        "loser": match.user_2
                    })
                    requests.post(
                        url, data=payload, headers=headers, 
                        auth=(tkn, 'unused')
                    )
    requests.post(urlgf, data=payloadgf, headers=headers, auth=(tkn, 'unused'))
    requests.post(urlgfr, data=payloadgfr, headers=headers, auth=(tkn, 'unused'))



# purge all tables first
db.session.close()
def purge(Model):
    [db.session.delete(row) for row in Model.query.all()]

for Model in [BracketModel, TournamentModel, MatchModel, RoundModel, UserModel]:
    purge(Model)
db.session.commit()

url = 'http://127.0.0.1:5000/api/users'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

# post miguel
payload = json.dumps({
    "username":"miguel",
    "password":"python",
    "email":"miguel@gmail.com"
})

r = requests.post(url, data=payload, headers=headers)

# post the rest of the users
users = [
    ('A', 'TPN@example.com'),
    ('B', 'AngryFalco@example.com'),
    ('C', 'Sunrisebanana@example.com'),
    ('D', 'Ptolemy@example.com'),
    ('E', 'Vik@example.com'),
    ('F', 'Kevin@example.com'),
    ('G', 'Spaceghost@example.com'),
    ('H', 'Burnaby@example.com'),
]

for username, email in users:
    payload = json.dumps({
        "username":username,
        "password":username.lower(),
        "email":email.lower()
    })

    r = requests.post(url, data=payload, headers=headers)

# get miguel's token
url = 'http://127.0.0.1:5000/api/token'
r = requests.get(url, auth=('miguel', 'python'))
tkn = json.loads(r.content)['token']

# miguel creates tournament\
# Fall Charity LAN 2018 Melee Singles users
N_COMPETITORS = 8
seeds = [i+1 for i in range(N_COMPETITORS)]
usernames = [
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
]
np.random.shuffle(usernames)
np.random.shuffle(seeds)

tuple_list = [(usernames[i], seeds[i]) for i in range(N_COMPETITORS)]

# create a json payload from the tuple list
url = 'http://127.0.0.1:5000/api/created-tournaments/'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
payload = json.dumps({
    "users":usernames,
    "seeds":seeds,
    "tournament_name":"Fall Charity LAN 2018 Melee Singles"
})
r = requests.post(url, data=payload, headers=headers, auth=("miguel", 'python'))
print(r.content)
tournament = \
    TournamentModel \
        .query \
        .filter_by(id=r.json().get("tournament_id")) \
        .first_or_404()

# get user's tkn
username = 'C'
url = 'http://127.0.0.1:5000/api/token'
r = requests.get(url, auth=(username, username.lower()))
c_tkn = json.loads(r.content)['token']

# user can't enter scores
handle_progression(tournament, c_tkn)

# TO (miguel) can enter scores
handle_progression(tournament, tkn)

# print all the tables for good measure

# Create the connection
cnx = sqlite3.connect(r'./app.db')

q = \
"""
    select * from user where
    username like '%TPN%'
"""
q = \
"""
    select * from user
"""
# create the dataframe from a query

# print('#'*68)
# print()

# print('Users\' table')
# df = pd.read_sql_query(q, cnx)
# print(df)
# print()
# for table in ['tournament', 'bracket', 'bracket_entrants', 'round', 'match']:
#     print('#'*68)
#     print()

#     print(f'{table} table')
#     print(pd.read_sql_query(f'select * from {table}', cnx))
#     print()