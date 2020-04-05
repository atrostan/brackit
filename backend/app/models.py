from datetime import datetime
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, 
    BadSignature, 
    SignatureExpired
)

# many to many relationship between User and Bracket
bracket_entrants = \
	db.Table(
		'bracket_entrants',
		db.Column('user_id', db.Integer, db.ForeignKey('user.id'), 
			primary_key=True),
		db.Column('bracket_id', db.Integer, db.ForeignKey('bracket.id'),
			primary_key=True)
	)

class Lobby(db.Model):
	__tablename__ = 'lobby'
	id = db.Column(db.Integer, primary_key=True)
	tournament_name = db.Column(db.String(64))
	tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
	to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	to = db.relationship('User', uselist=False, foreign_keys=[to_id])

	# impose a unique constraint on lobbies using the TO AND Tname cols
	__table_args__ = (
		db.UniqueConstraint(
			'tournament_name', 
			'to_id', 
			name='_tournament_org_name_uc'
		),
	)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	role = db.Column(db.String(10))
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	brackets = db.relationship('Bracket', secondary=bracket_entrants,
		backref='user_brackets', lazy=True)

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return f'<User {self.username}>'

	def generate_auth_token(self, expiration=3600):
		s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'id': self.id})

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None # valid token, but expired
		except BadSignature:
			return None # invalid token
		user = User.query.get(data['id'])
		return user

class LobbySeed(db.Model):
	__tablename__ = 'lobby_seeds'

	id = db.Column('id', db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
	lobby_id = db.Column(db.Integer, db.ForeignKey('lobby.id'))
	seed = db.Column(db.Integer)

	lobby = db.relationship(Lobby, backref="lobby_seeds")
	user = db.relationship(User, backref="lobby_seeds")

class Tournament(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	n_entrants = db.Column(db.Integer)
	name = db.Column(db.String(64))
	organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	finished = db.Column(db.Boolean, default=False)

	# 1 to many relationship between tournament and bracket
	brackets = db.relationship('Bracket', backref='tournament', lazy=True)

	# impose a unique constraint on tournaments using the organizer_id AND 
	# name columns
	# i.e. a user can't create have more than 1 tournament going 
	# __table_args__ = (
	# 	db.UniqueConstraint(
	# 		'tournament_name', 
	# 		'to_id', 
	# 		name='_tournament_org_name_uc'
	# 	),
	# )

class Bracket(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	bracket_type = db.Column(db.String(20))
	users = db.relationship('User', secondary=bracket_entrants,
						backref='bracket_users', lazy='select', passive_deletes=True)
	tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'),
						nullable=False)

	# 1 to many relationship between bracket and rounds
	rounds = db.relationship('Round', backref='bracket', lazy=True)

	def __repr__(self):
		return f'<{self.bracket_type} bracket: tournament {self.tournament_id}>'


class Round(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	number = db.Column(db.Integer)
	winners = db.Column(db.Boolean)
	bracket_id = db.Column(db.Integer, db.ForeignKey('bracket.id'),
						nullable=True)

	# 1 to many relationship between round and matches
	matches = db.relationship('Match', backref='round', lazy=True)

	def __repr__(self):
		return f'round {self.number} in bracket {self.bracket_id}'


class Match(db.Model):
	__tablename__ = 'match'
	id = db.Column(db.Integer, primary_key=True)
	uuid = db.Column(db.Text(length=36), index=True)

	# 1 to 2 relationship between match and users
	user_1 = db.Column(db.Integer, db.ForeignKey('user.id'))
	user_1_score = db.Column(db.Integer)

	user_2 = db.Column(db.Integer, db.ForeignKey('user.id'))
	user_2_score = db.Column(db.Integer)

	# match winner - if None, match is ongoing
	winner = db.Column(db.Integer, db.ForeignKey('user.id'))

	round_id = db.Column(db.Integer, db.ForeignKey('round.id'),
					nullable=False)

	# self refer to next match for winner and loser
	winner_advance_to = db.Column(db.Integer, db.ForeignKey('match.id'))
	loser_advance_to = db.Column(db.Integer, db.ForeignKey('match.id'))

	winner_to = db.relationship(
		"Match",
		primaryjoin="Match.winner_advance_to == remote(Match.id)",
		uselist=False, 
		post_update=True
	)

	loser_to = db.relationship(
		'Match',
		primaryjoin="Match.loser_advance_to == remote(Match.id)",
		uselist=False, 
		post_update=True
	)

	u1 = db.relationship("User", foreign_keys='Match.user_1')
	u2 = db.relationship("User", foreign_keys='Match.user_2')
	match_winner = db.relationship('User', foreign_keys='Match.winner')

	def input_user_to_match(self, entrant):
		if self.user_1 == None:
			self.user_1 = entrant
		elif self.user_2 == None:
			self.user_2 = entrant
		else:
			print(f"Match {str(self.id)} is full! Error")

	def __repr__(self):
		return f'<match {self.id} between {self.user_1} and {self.user_2}>'

	def get_TO(self,):
		"""Get the Match's Tournament Organizer
		"""

		# match = MatchModel.query.filter_by(id=m_id).first_or_404()
		r_id = self.round_id
		round = Round.query.filter_by(id=r_id).first_or_404()
		b_id = round.bracket_id
		bracket = Bracket.query.filter_by(id=b_id).first_or_404()
		t_id = bracket.tournament_id
		tournament = Tournament.query.filter_by(id=t_id).first_or_404()
		return tournament.organizer_id

# marshmellow schemas (needed to de/serialize to json)
class UserSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = User
		include_relationships = True
		load_instance = True  # Optional: deserialize to model instances

class TournamentSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = Tournament
		include_relationships = True
		load_instance = True  # Optional: deserialize to model instances

class BracketSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = Bracket
		include_relationships = True
		load_instance = True  # Optional: deserialize to model instances

class RoundSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = Round
		include_relationships = True
		load_instance = True  # Optional: deserialize to model instances

class MatchSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = Match
		include_relationships = True
		load_instance = True  # Optional: deserialize to model instances

class LobbySchema(SQLAlchemyAutoSchema):
	class Meta:
		model = Lobby
		# include_relationships = True
		load_instance = True  # Optional: deserialize to model instances

class LobbySeedSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = LobbySeed
		many = True
		include_relationships = True
		load_instance = True  # Optional: deserialize to model instances


@login.user_loader
def load_user(id):
	return User.query.get(int(id))


