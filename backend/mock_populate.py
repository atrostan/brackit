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
url = 'http://127.0.0.1:5000/api/token'
r = requests.get(url, auth=('miguel', 'python'))
tkn = json.loads(r.content)['token']

# miguel creates tournament\
# Fall Charity LAN 2018 Melee Singles users
N_COMPETITORS = 8
seeds = [i+1 for i in range(N_COMPETITORS)]
usernames = [
    'TPN',
    'AngryFalco',
    'Sunrisebanana',
    'Ptolemy',
    'Vik',
    'Kevin',
    'Spaceghost',
    'Burnaby',
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
r = requests.post(url, data=payload, headers=headers, auth=(tkn, 'unused'))
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