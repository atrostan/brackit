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
    content = {'Success' : f'{current_user.username} logged in','id' : current_user.id}
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
                'Success' : 'Lobby created',
                'lobby_id' : lobby.id,
                'tournament_name' : tournament_name
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

@app.route('/api/lobby/<int:lobby_id>/create-tournament/', methods=['POST'])
@auth.login_required
def create_tournament_from_lobby(lobby_id):
    if request.method == 'POST':

        # verify that TO is attempting to access lobby
        uid = g.user.id
        uname = g.user.username

        try:
            lobby = LobbyModel.query.filter_by(id=lobby_id).first_or_404()
            if uid != lobby.to_id:
                key = 'Unauthorized'
                val = \
                    f'{g.user.username} cannot create a tournament ' + \
                    'using this lobby'
                content = {key : val}
                return content, status.HTTP_401_UNAUTHORIZED

        except NotFound as e:
            key = str(e).split(':')[0]
            val = f'lobby {lobby_id} does not exist'
            content = {key : val}
            return content, status.HTTP_404_NOT_FOUND

        # get all competitors in the lobby
        lobby_entrants = LobbySeed.query.filter_by(lobby_id=lobby_id).all()
        # construct a list of user_id, seed pairs
        tuple_list = [(e.user.username, e.seed) for e in lobby_entrants]
        bracket_type = BracketTypes.DOUBLE_ELIMINATION
        tournament_name = lobby.tournament_name
        # contruct a tournament object
        t = Tournament(tuple_list, bracket_type)
        t_id = t.post_to_db(tournament_name, uname)

        # set this lobby's tournament_id
        lobby.tournament_id = t_id

        for r in t.bracket.rounds:
            for m in r.matches:
                m.post_self_refs()

        # delete the lobby 
        LobbyModel.query.filter_by(id=lobby_id).delete()
        LobbySeed.query.filter_by(lobby_id=lobby_id).delete()
        db.session.commit()

        key = 'Success'
        val = f'Created tournament {t_id}'
        content = {key : val}

        return content, status.HTTP_200_OK

# tournament creation endpoint
@app.route('/api/created-tournaments/', methods=['GET', 'POST'])
@auth.login_required
def create_tournament_1():

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
    matchRound = RoundModel.query.filter_by(id=match.round_id).first_or_404()
    if matchRound.number is 1:
        adjacentId = id+1 if (match.id % 2 is not 0) else id-1
        adjacentmatch = MatchModel.query.filter_by(id=adjacentId).first()
    else: 
        adjacentmatch = None
    # ensure that TO is inputting scores and winners
    if g.user.id != match.get_TO():
        content = {
            'Access Denied': 'Only Tournament Organizers can report matches'
        }
        return content, status.HTTP_403_FORBIDDEN

    if (match.winner is not None):
        content = {f'Match {str(id)} has already been completed': 'it cannot be reported'}
        return content, status.HTTP_406_NOT_ACCEPTABLE

    if (match.user_1 is None or match.user_2 is None):
        content = {f'Match {str(id)} has not been reached': 'it cannot be reported'}
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
    if match.loser_to is not None:
        match.loser_to.input_user_to_match(loser_id)

        # Handle byes in losers bracket
        prev_match_winners = MatchModel.query.filter_by(loser_advance_to=match.loser_to.id).all()
        if match in prev_match_winners:
            prev_match_winners.remove(match)
        prev_match_losers = MatchModel.query.filter_by(winner_advance_to=match.loser_to.id).all()
        if match in prev_match_losers:
            prev_match_losers.remove(match)
        for prev_match in prev_match_winners:
            if (match.loser_to.user_2 is None and prev_match.user_1_score is not None):
                match.loser_to.winner = loser_id
                match.loser_to.user_1_score = 0
                match.loser_to.user_2_score = -1
                match.loser_to.winner_to.input_user_to_match(loser_id)
                db.session.add(match.loser_to.winner_to)
        for prev_match in prev_match_losers:
            if (match.loser_to.user_2 is None and prev_match.user_1_score is not None):
                match.loser_to.winner = loser_id
                match.loser_to.user_1_score = 0
                match.loser_to.user_2_score = -1
                match.loser_to.winner_to.input_user_to_match(loser_id)
                db.session.add(match.loser_to.winner_to)
            if (match.loser_to.user_2 is None and prev_match.user_1 is None and prev_match.user_2 is None and prev_match.user_2_score is None):
                match.loser_to.winner = loser_id
                match.loser_to.user_1_score = 0
                match.loser_to.user_2_score = -1
                match.loser_to.winner_to.input_user_to_match(loser_id)
                db.session.add(match.loser_to.winner_to)

                prev_match.winner = prev_match.user_1
                prev_match.user_1_score = 0
                prev_match.user_2_score = -1
                db.session.add(prev_match)
        db.session.add(match.loser_to)
    
    db.session.add(match)
    db.session.commit()

    match_schema = MatchSchema()
    return match_schema.dump(match)

@app.route('/api/user/<int:user_id>/tournaments/')
def user_tournaments(user_id):
    """return all the tournaments this user has created
    
    Arguments:
        user_id {int} 
    """
    try:
        user = UserModel.query.filter_by(id=user_id).first_or_404()
    except NotFound as e:
        key = str(e).split(':')[0]
        val = f'user {user_id} does not exist'
        content = {key : val}
        return content, status.HTTP_404_NOT_FOUND

    tournament_schema = TournamentSchema()
    tournaments = \
        TournamentModel \
            .query \
            .filter_by(organizer_id=user.id) \
            .all()
    tournaments = [tournament_schema.dump(t) for t in tournaments]
    return json.dumps(tournaments)

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
    
@app.route('/api/user/<int:user_id>/modify/', methods=['POST'])
@auth.login_required
def modify_user(user_id):
    # verify that modifying user has credentials
    curr_uid = g.user.id

    try:
        user = UserModel.query.filter_by(id=user_id).first_or_404()
        if curr_uid != user.id:
            key = 'Unauthorized'
            val = \
                f'{g.user.username} is not authorized to modify this user'
            content = {key : val}
            return content, status.HTTP_401_UNAUTHORIZED

    except NotFound as e:
        key = str(e).split(':')[0]
        val = f'user {user_id} does not exist; it cannot be modified'
        content = {key : val}
        return content, status.HTTP_404_NOT_FOUND

    try:
        new_uname = request.json.get('username')
        new_about_me = request.json.get('about_me')
    except Exception as e:
        return str(e), status.HTTP_400_BAD_REQUEST

    if UserModel.query.filter_by(username=new_uname).first() is None:

        if new_uname is None and new_about_me is None:
            return 'User modification fields empty', status.HTTP_204_NO_CONTENT

        elif new_uname is None:
            # user.update(dict(about_me=new_about_me))
            user.about_me = new_about_me

            db.session.commit()
            key = 'Partial Content'
            val = 'Username field empty; updated about_me'
            s = 'About me field empty;' + \
                f'Updated username from {user.username} to {new_uname}'
            return {key:val}, status.HTTP_206_PARTIAL_CONTENT

        elif new_about_me is None:
            # user.update(dict(username=new_uname))
            user.username = new_uname

            key = 'Partial Content'
            val = 'About me field empty; updated username'

            db.session.commit()

            return {key:val}, status.HTTP_206_PARTIAL_CONTENT
        
        else:
            # user.update(dict(username=new_uname, about_me=new_about_me))
            user.about_me = new_about_me
            user.username = new_uname

            db.session.commit()

            key = 'Success'
            val = 'Updated username and about_me'
            return {key:val}, status.HTTP_202_ACCEPTED
    else:
        key = 'Invalid Username'
        val = \
            f'{new_uname} Already Taken'
        content = {key : val}
        return content, status.HTTP_409_CONFLICT


@app.route('/api/user/<int:id>')
def get_user(id):
    user_schema = UserSchema()
    user = UserModel.query.filter_by(id=id).first_or_404()
    dump_data = user_schema.dump(user)
    return dump_data

@app.route('/api/tournament/<int:id>/full')
def tournament_full(id):
    tournament_schema = TournamentSchema()
    tournament = TournamentModel.query.filter_by(id=id).first_or_404()
    tournament_data = tournament_schema.dump(tournament)
    for i in range(len(tournament_data.get("brackets"))):
        # bracket_schema = BracketSchema()
        # bracket = BracketModel.query.filter_by(tournament_data.get("brackets")[i]).first_or_404()
        # bracket_data = bracket_schema.dump(bracket)
        bracket_data = bracket(tournament_data.get("brackets")[i])
        for j in range(len(bracket_data.get("rounds"))): 
            round_data = round(bracket_data.get("rounds")[j])
            for k in range(len(round_data.get("matches"))):
                match_data = match(round_data.get("matches")[k])
                if match_data["u1"] is not None:
                    match_data["u1"] = get_user(match_data.get("u1"))
                if match_data["u2"] is not None:
                    match_data["u2"] = get_user(match_data.get("u2"))
                round_data.get("matches")[k] = match_data
            bracket_data.get("rounds")[j] = round_data
        for j in range(len(bracket_data.get("users"))):
            bracket_data.get("users")[j] = get_user(bracket_data.get("users")[j])
        tournament_data.get("brackets")[i] = bracket_data
    return tournament_data

@app.route('/api/tournament/<int:id>')
def tournament(id):
    tournament_schema = TournamentSchema()
    tournament = TournamentModel.query.filter_by(id=id).first_or_404()
    dump_data = tournament_schema.dump(tournament)
    return dump_data
    
@app.route('/api/bracket/<int:id>/winners_losers_rounds')
def bracket_winners_losers_rounds(id):
    round_schema = RoundSchema()
    rounds = RoundModel.query.filter_by(bracket_id=id).all()
    dump_data = {
        "winners_rounds":[],
        "losers_rounds":[]
    }
    for r in rounds:
        if r.winners == True:
            dump_data["winners_rounds"].append(round_schema.dump(r))
        else:
            dump_data["losers_rounds"].append(round_schema.dump(r))

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



