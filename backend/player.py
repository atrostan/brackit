class Entrant: 
    def __init__(self, profile, seed):
        self.profile = profile
        self.seed = seed
    
    def __init__(self, tag, seed):
        self.profile = Profile(tag)
        self.seed = seed

class Profile: 
    def __init__(self, tag):
        self.tag = tag