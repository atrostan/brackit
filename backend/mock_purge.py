from app import db
from app.models import (
    Bracket,
    Match,
    Round,
    Tournament,
    User, 
)

def purge(Model):
    [db.session.delete(row) for row in Model.query.all()]

purge(User)

db.session.commit()