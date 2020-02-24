#!/usr/bin/env python
# coding: utf-8

# In[1]:


# get_ipython().run_line_magic('load_ext', 'autoreload')
# get_ipython().run_line_magic('autoreload', '2')
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
from player import User


# In[2]:


import uuid


# In[3]:


str(uuid.uuid4())


# In[4]:


db.session.close()


# In[5]:


def purge(Model):
    [db.session.delete(row) for row in Model.query.all()]


# In[6]:


# purge all tables first

for Model in [BracketModel, TournamentModel, MatchModel, RoundModel, UserModel]:
    purge(Model)
db.session.commit()


# In[7]:


# add all users to users table
users = [
    UserModel(username='TPN', email='TPN@example.com'.lower()), 
    UserModel(username='AngryFalco', email='AngryFalco@example.com'.lower()), 
    UserModel(username='Sunrisebanana', email='Sunrisebanana@example.com'.lower()), 
    UserModel(username='Ptolemy', email='Ptolemy@example.com'.lower()), 
    UserModel(username='Vik', email='Vik@example.com'.lower()), 
    UserModel(username='Kevin', email='Kevin@example.com'.lower()), 
    UserModel(username='Spaceghost', email='Spaceghost@example.com'.lower()), 
    UserModel(username='Burnaby', email='Burnaby@example.com'.lower()), 
]
[db.session.add(u) for u in users]
db.session.commit()


# In[8]:


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


# In[9]:

user_list = [User(usernames[i]) for i in range(N_COMPETITORS)]
tuple_list = [(user_list[i], seeds[i]) for i in range(N_COMPETITORS)]


# In[10]:


btype = BracketTypes.DOUBLE_ELIMINATION
tournament_name = 'Fall Charity LAN 2018 Melee Singles'
t = Tournament(tournament_name, None, tuple_list, btype)


# In[11]:



# initial post to db
t.post_to_db()


# In[12]:


# post self references in matches separately
# for r in t.bracket.rounds:
#     for m in r.matches:
#         m.post_self_refs()


# In[13]:


import sqlite3
import pandas as pd

# Create the connection
cnx = sqlite3.connect(r'./app.db')

q = """
    select * from user where
    username like '%TPN%'
"""
q = """
    select * from user
"""
# create the dataframe from a query
df = pd.read_sql_query(q, cnx)
df


# In[14]:


pd.read_sql_query('select * from tournament', cnx)


# In[15]:


pd.read_sql_query('select * from bracket', cnx)


# In[16]:


pd.read_sql_query('select * from bracket_entrants', cnx)


# In[17]:


pd.read_sql_query('select * from round', cnx)


# In[18]:


df = pd.read_sql_query('select * from match', cnx)
df
# df.loc[df['uuid'] == '94de92a2-13ac-4e9a-9bf2-78636100a7b1']


# In[ ]:










































































































