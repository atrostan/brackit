from app import db
from app.models import User as UserModel

class User: 
    def __init__(self, username, email, password_hash, posts, about_me, last_seen, brackets):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.posts = posts
        self.about_me = about_me
        self.last_seen = last_seen
        self.brackets = brackets
    def __init__(self, username):
        self.username = username
        self.email = None
        self.password_hash = None
        self.posts = None
        self.about_me = None
        self.last_seen = None
        self.brackets = None
    def post_to_db(self):
        u_model = UserModel(
            username = self.username,
            email = self.email,
            password_hash = self.password_hash,
            about_me = self.about_me
        )
        try:
            db.session.add(u_model); db.session.commit()
        except:
            print("Username " + self.username +" already exists in database.")