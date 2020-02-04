from app import db
from app.models import (
    Bracket,
    Match,
    Round,
    Tournament,
    User, 
)

def purge_model(Model):
    [db.session.delete(row) for row in Model.query.all()]

purge_model(User)

db.session.commit()