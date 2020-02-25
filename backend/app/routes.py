from flask import (
    abort,
    flash,
    g, 
    redirect, 
    render_template, 
    url_for,
    jsonify
)
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

from app.models import (
    Bracket,
    BracketSchema,
    Match,
    MatchSchema,
    Round, 
    RoundSchema,
    Tournament, 
    TournamentSchema,
    User, 
    UserSchema,
)

from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from datetime import datetime

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

# @app.route('/edit_profile', methods=['GET', 'POST'])
# @login_required
# def edit_profile():
#     form = EditProfileForm()
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         current_user.about_me = form.about_me.data
#         db.session.commit()
#         flash('Your changes have been saved.')
#         return redirect(url_for('edit_profile'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html', title='Edit Profile',
#                             form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("index.html", title='Home Page', posts=posts)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
#         login_user(user, remember=form.remember_me.data)
#         next_page = request.args.get('next')
#         if not next_page or url_parse(next_page).netloc != '':
#             next_page = url_for('index')
#         return redirect(next_page)
#     # return jsonify(form.)
#     return render_template('login.html', title='Sign In', form=form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# validation of user credentials - callback invoked whenever 
# @auth.login_required decorator is used
@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
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
    if User.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User(username = username, email=email)
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

@app.route('/api/user/<int:id>')
def get_user(id):
    user_schema = UserSchema()
    user = User.query.filter_by(id=id).first_or_404()
    dump_data = user_schema.dump(user)
    return dump_data

@app.route('/api/tournament/<id>')
def tournament(id):
    tournament_schema = TournamentSchema()
    tournament = Tournament.query.filter_by(id=id).first_or_404()
    dump_data = tournament_schema.dump(tournament)
    return dump_data

@app.route('/api/bracket/<id>')
def bracket(id):
    bracket_schema = BracketSchema()
    bracket = Bracket.query.filter_by(id=id).first_or_404()
    dump_data = bracket_schema.dump(bracket)
    return dump_data

@app.route('/api/round/<id>')
def round(id):
    round_schema = RoundSchema()
    round = Round.query.filter_by(id=id).first_or_404()
    dump_data = round_schema.dump(round)
    return dump_data

@app.route('/api/match/<id>')
def match(id):
    match_schema = MatchSchema()
    match = Match.query.filter_by(id=id).first_or_404()
    dump_data = match_schema.dump(match)
    return dump_data
