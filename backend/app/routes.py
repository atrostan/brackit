from flask import (
    abort,
    flash,
    g, 
    redirect, 
    render_template, 
    url_for,
    jsonify
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
from app.models import Match as MatchModel
from app.models import Round as RoundModel
from app.models import Tournament as TournamentModel
from app.models import User as UserModel

from app.models import (
    BracketSchema,
    MatchSchema,
    RoundSchema,
    TournamentSchema,
    UserSchema,
)

from tournament import (
    BracketTypes,
    Tournament,
    Match
)
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from datetime import datetime

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

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
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

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

        print(tuple_list)
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




