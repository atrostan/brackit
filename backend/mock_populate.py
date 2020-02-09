from app import db
from app.models import (
    Bracket,
    Match,
    Round,
    Tournament,
    User, 
)

# Fall Charity LAN 2018 Melee Singles users
users = [
    User(username='TPN', email='TPN@example.com'.lower()), 
    User(username='AngryFalco', email='AngryFalco@example.com'.lower()), 
    User(username='Sunrisebanana', email='Sunrisebanana@example.com'.lower()), 
    User(username='Ptolemy', email='Ptolemy@example.com'.lower()), 
    User(username='Vik', email='Vik@example.com'.lower()), 
    User(username='Kevin', email='Kevin@example.com'.lower()), 
    User(username='Spaceghost', email='Spaceghost@example.com'.lower()), 
    User(username='Burnaby', email='Burnaby@example.com'.lower()), 
]

[db.session.add(u) for u in users]
db.session.commit()