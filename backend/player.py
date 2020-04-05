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
