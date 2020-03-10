from flask import (
    abort,
    flash,
    g, 
    redirect, 
    render_template, 
    url_for,
    jsonify, 
    session
)
from flask_api import status
from app import app
from app.forms import (
    EditProfileForm,
    LoginForm
)

from flask_login import (
    current_user, 
    login_required,
    login_user, 
    logout_user, 
)

from app.models import Bracket as BracketModel
from app.models import Lobby as LobbyModel
from app.models import Match as MatchModel
from app.models import Round as RoundModel
from app.models import Tournament as TournamentModel
from app.models import User as UserModel
# from app.models import LobbySeed as LobbySeedModel

from app.models import (
    BracketSchema,
    LobbySchema,
    MatchSchema,
    RoundSchema,
    TournamentSchema,
    UserSchema,
    LobbySeedSchema,
    LobbySeed
)

from tournament import (
    BracketTypes,
    Tournament,
    Match
)

from flask import request
from werkzeug.urls import url_parse
from werkzeug.exceptions import NotFound
from app import db
from app.forms import RegistrationForm
from datetime import datetime
from sqlalchemy import exc
from flask_httpauth import HTTPBasicAuth

import sqlite3, json

auth = HTTPBasicAuth()

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# @app.before_request
# def load_user():
#     print(vars(session))
#     if session["id"]:
#         user = UserModel.query.filter_by(username=session["id"]).first()
#     else:
#         user = {"name": "Guest"}  # Make it better, use an anonymous User instead

#     g.user = user

# validation of user credentials - callback invoked whenever 
# @auth.login_required decorator is used
@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = UserModel.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = UserModel.query.filter_by(username = username_or_token).first()
        if not user or not user.check_password(password):
            return False
    g.user = user
    return True

# register user endpt
@app.route('/api/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    if username is None or password is None:
        abort(400) # missing arguments
    if UserModel.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = UserModel(username = username, email=email, role='User')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username }), 201, {'location': url_for('get_user', id = user.id, _external = True)}


# user login endpt
@app.route('/api/login')
@auth.login_required
def user_login():
    # print(g.user)
    login_user(g.user)
    content = {'Success' : f'{current_user.username} logged in'}
    return content, status.HTTP_200_OK

@app.route('/api/logout')
@auth.login_required
def logout():
    # print(g.user)
    # print(current_user)
    # username = current_user.username
    logout_user()
    g.user = None
    content = {'Success' : 'logged out'}
    return content, status.HTTP_200_OK

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

@app.route('/api/create/lobby/', methods=['POST'])
@auth.login_required
def create_lobby():
    if request.method == 'POST':
        to_id = g.user.id
        tournament_name = request.json.get('tournament_name')

        lobby = LobbyModel(
            tournament_name=tournament_name,
            to_id=to_id,
        )

        try:
            db.session.add(lobby) 
            db.session.commit()
            content = {
            'Lobby Created': f'Lobby created for tournament: {tournament_name}'
            }
            return content, status.HTTP_201_CREATED

        except exc.IntegrityError:
            key = 'Unique Constraint Failed'
            val = \
                f'User \"{to_id}\" already created tournament \"{tournament_name}\"'
            content = {
                key : val 
            }
            return content, status.HTTP_406_NOT_ACCEPTABLE

@app.route('/api/lobby/<int:lobby_id>/add-user/', methods=['POST'])
@auth.login_required
def add_user_to_lobby(lobby_id):    
    # print(g.user)
    if request.method == 'POST':

        # verify that TO is attempting to access lobby
        uid = g.user.id
        # print(f'user whose tryna add {uid}')
        # print(f'{vars(current_user)}')

        try:
            lobby = LobbyModel.query.filter_by(id=lobby_id).first_or_404()
            if uid != lobby.to_id:
                key = 'Unauthorized'
                val = f'{g.user.username} cannot add entrants to this lobby'
                content = {key : val}
                return content, status.HTTP_401_UNAUTHORIZED

        except NotFound as e:
            key = str(e).split(':')[0]
            val = f'lobby {lobby_id} does not exist'
            content = {key : val}
            return content, status.HTTP_404_NOT_FOUND

        name = request.json.get('username')
        role = request.json.get('role')
        seed = request.json.get('seed')

        # add user to lobby_seeds table
        if role == 'User':
            try:
                # get user id
                user = \
                    UserModel \
                        .query \
                        .filter_by(username=name, role=role) \
                        .first_or_404()
                # set this user's seed in this lobby
                ls = LobbySeed(user_id=user.id, lobby_id=lobby.id, seed=seed)

                try:
                    db.session.add(ls)
                    db.session.commit()
                except exc.IntegrityError:
                    db.session.rollback()
                    key = 'Unique Constraint Failed'
                    val = \
                        f'{user} already in {lobby}'
                    content = {
                        key : val 
                    }
                    return content, status.HTTP_406_NOT_ACCEPTABLE
                    
                key = 'Added'; val = f'{role} {name} to lobby {lobby_id}'
                content = {key : val}

                return content, status.HTTP_202_ACCEPTED

            except NotFound as e:
                key = str(e).split(':')[0]
                val = \
                    f'{role} {name} not found'
                content = {key : val}
                return content, status.HTTP_404_NOT_FOUND

        elif role == 'Guest':
            # create Guest user
            # check that username isn't taken
            if UserModel.query.filter_by(username=name).first() is None:
                user = UserModel(username=name, role=role,)
                db.session.add(user)
                db.session.commit()

                ls = LobbySeed(user_id=user.id, lobby_id=lobby.id, seed=seed)

                db.session.add(ls)
                db.session.commit()
                # set this user's seed in this lobby
                # print(ls)
                # lobby.entrants.append(user)

                key = 'Added'; val = f'{role} {name} to lobby {lobby_id}'
                content = {key : val}

                return content, status.HTTP_202_ACCEPTED

            else:
                key = 'Invalid Username'
                val = \
                    f'{name} Already Taken'
                content = {key : val}
                return content, status.HTTP_409_CONFLICT
        
        # key = 'Success'
        # if role == 'Guest': val = f'created {role} user {name}'
        # else: val = f'added {role} {name} to lobby {1}'
        # content = {key : val}
        # return content, status.HTTP_200_OK

# tournament creation endpoint
@app.route('/api/created-tournaments/', methods=['GET', 'POST'])
@auth.login_required
def create_tournament():

    # create a new tournament
    if request.method == 'POST':
        users = request.json.get('users')
        seeds = request.json.get('seeds')
        tournament_name = request.json.get('tournament_name')
        bracket_type = BracketTypes.DOUBLE_ELIMINATION
        TO = g.user.username

        tuple_list = [(u, s) for u, s in zip(users, seeds)]
        t = Tournament(tuple_list, bracket_type)

        t_id = t.post_to_db(tournament_name, TO)

        # post self references in matches separately
        for r in t.bracket.rounds:
            for m in r.matches:
                m.post_self_refs()
        return jsonify({'tournament_id': t_id})
    else:
        # return jsonify({ 'username': user.username }), 201, {'location': url_for('get_user', id = user.id, _external = True)}
        return

@app.route('/api/match/<int:id>/report-match', methods=['POST'])
@auth.login_required
def report_match(id):
    match = MatchModel.query.filter_by(id=id).first_or_404()

    # ensure that TO is inputting scores and winners
    if g.user.id != match.get_TO():
        content = {
            'Access Denied': 'Only Tournament Organizers can report matches'
        }
        return content, status.HTTP_403_FORBIDDEN

    if match.user_1 is None or match.user_2 is None:
        content = {'This match has not been reached': 'it cannot be reported'}
        return content, status.HTTP_406_NOT_ACCEPTABLE
    entrant1_score = request.json.get('entrant1_score')
    entrant2_score = request.json.get('entrant2_score')
    winner_id = request.json.get('winner')
    loser_id = request.json.get('loser')
    match.user_1_score = entrant1_score
    match.user_2_score = entrant2_score
    match.winner = winner_id
    if match.winner_to is not None:
        match.winner_to.input_user_to_match(winner_id)
        db.session.add(match.winner_to)
    if (match.loser_to is not None):
        match.loser_to.input_user_to_match(loser_id)
        db.session.add(match.loser_to)
    
    db.session.add(match)
    db.session.commit()

    match_schema = MatchSchema()
    return match_schema.dump(match)

@app.route('/api/user/<int:id>/winsandlosses')
def winsandlosses(id):
    user = UserModel.query.filter_by(id=id).first_or_404()
    user_brackets = user.brackets
    wins_losses = []
    alreadyin = False
    for bracket in user_brackets:
        for round in bracket.rounds:
            for match in round.matches:
                if match.u1 is None or match.u2 is None or match.winner is None:
                    continue
                if match.user_2 == id:
                    for winloss in wins_losses:
                        if match.user_1 == winloss.get("User"):
                            alreadyin = True
                            if match.user_1 == match.winner:
                                winloss.update({"Losses": winloss.get("Losses") + 1})
                            elif match.winner == id:
                                winloss.update({"Wins": winloss.get("Wins") + 1})
                    if not alreadyin:
                        if match.user_1 == match.winner:
                            wins_losses.append({
                                        "User": match.user_1, 
                                        "Wins": 0, 
                                        "Losses": 1
                                    })
                        elif match.winner == id:
                            wins_losses.append({
                                        "User": match.user_1, 
                                        "Wins": 1, 
                                        "Losses": 0
                                    })
                if match.user_1 == id:
                    for winloss in wins_losses:
                        if match.user_2 == winloss.get("User"):
                            alreadyin = True
                            if match.user_2 == match.winner:
                                winloss.update({"Losses": winloss.get("Losses") + 1})
                            elif match.winner == id:
                                winloss.update({"Wins": winloss.get("Wins") + 1})
                    if not alreadyin:
                        if match.user_2 == match.winner:
                            wins_losses.append({
                                        "User": match.user_2, 
                                        "Wins": 0, 
                                        "Losses": 1
                                    })
                        elif match.winner == id:
                            wins_losses.append({
                                        "User": match.user_2, 
                                        "Wins": 1, 
                                        "Losses": 0
                                    })
    return jsonify(wins_losses)


@app.route('/api/user/<int:id>')
def get_user(id):
    user_schema = UserSchema()
    user = UserModel.query.filter_by(id=id).first_or_404()
    dump_data = user_schema.dump(user)
    return dump_data

@app.route('/api/tournament/<int:id>')
def tournament(id):
    tournament_schema = TournamentSchema()
    tournament = TournamentModel.query.filter_by(id=id).first_or_404()
    dump_data = tournament_schema.dump(tournament)
    return dump_data

@app.route('/api/bracket/<int:id>')
def bracket(id):
    bracket_schema = BracketSchema()
    bracket = BracketModel.query.filter_by(id=id).first_or_404()
    dump_data = bracket_schema.dump(bracket)
    return dump_data

@app.route('/api/round/<int:id>')
def round(id):
    round_schema = RoundSchema()
    round = RoundModel.query.filter_by(id=id).first_or_404()
    dump_data = round_schema.dump(round)
    return dump_data

@app.route('/api/match/<int:id>')
def match(id):
    match_schema = MatchSchema()
    match = MatchModel.query.filter_by(id=id).first_or_404()
    dump_data = match_schema.dump(match)
    return dump_data

@app.route('/api/lobby/<int:id>')
def lobby(id):
    lobby_schema = LobbySchema()
    lobby = LobbyModel.query.filter_by(id=id).first_or_404()
    dump_data = lobby_schema.dump(lobby)
    return dump_data

@app.route('/api/lobby/<int:id>/entrants')
def lobby_seeds(id):
    lobby_seed_schema = LobbySeedSchema()
    lobby = LobbySeed.query.filter_by(lobby_id=id).all()
    dump_data = [lobby_seed_schema.dump(item) for item in lobby]
    # print(dump_data)
    return json.dumps(dump_data)



