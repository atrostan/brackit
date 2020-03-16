from app import db
import numpy as np

from app.models import Tournament as TournamentModel
from app.models import Lobby as LobbyModel
from app.models import Bracket as BracketModel
from app.models import Match as MatchModel
from app.models import Round as RoundModel
from app.models import User as UserModel
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

db.session.close()

def purge(Model):
    [db.session.delete(row) for row in Model.query.all()]

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

for Model in Models:
    purge(Model)
db.session.commit()

cnx = sqlite3.connect(r'./app.db')

url = 'http://127.0.0.1:5000/api/users'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
payload = json.dumps({
    "username":"miguel",
    "password":"python",
    "email":"miguel@gmail.com"
})

r = requests.post(url, data=payload, headers=headers)

# log miguel in
url = 'http://127.0.0.1:5000/api/login'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
# payload = json.dumps({
#     "username":"miguel",
#     "password":"python",
#     "email":"miguel@gmail.com"
# })

r = requests.get(url, headers=headers, auth=('miguel', 'python'))
r.content

# log miguel out
url = 'http://127.0.0.1:5000/api/logout'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
# payload = json.dumps({
#     "username":"miguel",
#     "password":"python",
#     "email":"miguel@gmail.com"
# })

r = requests.get(url, headers=headers, auth=('miguel', 'python'))
r.content

url = 'http://127.0.0.1:5000/api/users'
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


url = 'http://127.0.0.1:5000/api/token'
r = requests.get(url, auth=('miguel', 'python'))
tkn = json.loads(r.content)['token']
tkn

# now this user can login with a token
url = 'http://127.0.0.1:5000/api/login'

r = requests.get(url, auth=(tkn, 'unused'))


# miguel creates lobby

url = 'http://127.0.0.1:5000/api/create/lobby/'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
payload = json.dumps({
    "tournament_name" : "miguel's tourneys"
})
r = requests.post(url, data=payload, headers=headers, auth=(tkn, 'unused'))
json.loads(r.content)

url = 'http://127.0.0.1:5000/api/token'
r = requests.get(url, auth=('miguel', 'python'))
tkn = json.loads(r.content)['token']
tkn

q = \
"""
    select * from user
"""

# posted a user
df = pd.read_sql_query(q, cnx)
df

users = df.username.values
np.random.shuffle(users)
import random

# miguel adds users to his lobby

url = 'http://127.0.0.1:5000/api/lobby/1/add-user/'
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
    

url = 'http://127.0.0.1:5000/api/lobby/1'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
# payload = json.dumps({
#     "username" : "AngryFalco",
#     "role" : "User"
# })
r = requests.get(url, headers=headers,)
json.loads(r.content)

# miguel adds a guest user

url = 'http://127.0.0.1:5000/api/lobby/1/add-user/'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

payload = json.dumps({
    "username" : "guestb",
    "role" : "Guest",
    "seed" : 10
})
r = requests.post(url, data=payload, headers=headers, auth=(tkn, 'unused'))
print(json.loads(r.content))

# log miguel out
url = 'http://127.0.0.1:5000/api/lobby/1/add-user/'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

# TPN tries to add his own guests to miguel's lobby
url = 'http://127.0.0.1:5000/api/lobby/1/add-user/'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

payload = json.dumps({
    "username" : "guestx",
    "role" : "Guest",
    "seed" : 1
})
r = requests.post(url, data=payload, headers=headers, auth=('TPN', 'tpn'))
print(json.loads(r.content))

UserModel \
    .query \
    .filter_by(username='guesta', role='Guest') \
    .first() is None

url = 'http://127.0.0.1:5000/api/lobby/1/entrants'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
# payload = json.dumps({
#     "username" : "AngryFalco",
#     "role" : "User"
# })
r = requests.get(url, headers=headers,)
content =  json.loads(r.content)
print(content)