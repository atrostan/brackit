from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# from OpenSSL import SSL
# context = SSL.Context(SSL.TLSv1_2_METHOD)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('server.crt')


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models