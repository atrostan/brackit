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

users2 = [
    ('a', 'TPN@exale.com'),
    ('b', 'AngryFao@example.com'),
    ('c', 'Sunrisnana@example.com'),
    ('d', 'Ptolemy@exmple.com'),
    ('e', 'Vik@exple.com'),
    ('f', 'Kevin@emple.com'),
    ('g', 'Spacest@example.com'),
    ('h', 'Burnaby@emple.com'),
]

for username, email in users:
    payload = json.dumps({
        "username":username,
        "password":username.lower(),
        "email":email.lower()
    })

    r = requests.post(url, data=payload, headers=headers)

for username, email in users2:
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

print('#'*68)
print()

print('Users\' table')
df = pd.read_sql_query(q, cnx)
print(df)
print()
for table in ['tournament', 'bracket', 'bracket_entrants', 'round', 'match']:
    print('#'*68)
    print()

    print(f'{table} table')
    print(pd.read_sql_query(f'select * from {table}', cnx))
    print()