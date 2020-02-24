from enum import Enum
from player import User
from app import db
import math

from app.models import Tournament as TournamentModel
from app.models import Bracket as BracketModel
from app.models import Match as MatchModel
from app.models import Round as RoundModel
from app.models import User as UserModel

import uuid

class BracketTypes(Enum):
    DOUBLEELIMINATION = 1


class Tournament:
    def __init__(self, tournament_name, organizer, bracket):
        self.tournament_name = tournament_name
        self.organizer = organizer
        self.bracket = bracket
        self.post_to_db()

    # expects an list of tuples for entrants (competitor name, seed)
    def __init__(self, tournament_name, organizer, entrants, bracketType):
        self.tournament_name = tournament_name
        self.organizer = organizer
        # convert a list of tuples (competitor name, seed) to an ordered
        # list to be consumed by Bracket constructor
        if len(entrants) > 0:
            if type(entrants[0]) == tuple:
                entrants = [t[0] for t in sorted(entrants, key=lambda x: x[1])]

        self.bracket = Bracket(entrants, bracketType)
        self.post_to_db()

    def post_to_db(self):
        """push tournament to db
        
        Arguments:
            tournament_name {string} -- tournament name
            TO {string} -- name of tournament organizer
        """

        # tournament organizer id
        o_id = UserModel.query.filter_by(username=self.organizer).first_or_404().id

        t_model = TournamentModel(
            n_entrants = len(self.bracket.entrants),
            name = self.tournament_name,
            organizer_id = o_id
        )

        db.session.add(t_model); db.session.commit()
        
        # post this tournament's bracket to db
        self.bracket.post_to_db(t_model)

        return


class Bracket:
    def __init__(self, entrants, bracketType):
        self.entrants = entrants
        self.bracketType = bracketType
        self.ceilPlayers = int(2**(math.ceil(math.log(len(self.entrants)))))
        if (bracketType == BracketTypes.DOUBLE_ELIMINATION):
            self.makeDoubleElimBracket()

    def post_to_db(self, tournament_model):
        u_models = \
            [UserModel.query.filter_by(username=u).first_or_404() for u \
            in self.entrants]
        
        b_model = BracketModel(
            bracket_type=self.bracketType.name,
            users=u_models,
            tournament=tournament_model,
        )

        db.session.add(b_model); db.session.commit()

        for round in self.rounds:
            round.post_to_db(b_model) 


        return
        

    def makeDoubleElimBracket(self):
        # grand finals + reset round
        self.numWinnersRounds = int(math.log(self.ceilPlayers, 2)+2)
        self.numLosersRounds = \
            int((math.log(self.ceilPlayers, 2)) +
                math.log(math.log(self.ceilPlayers, 2), 2))
        self.numTotalRounds = self.numLosersRounds + self.numWinnersRounds
        self.rounds = []
        for i in range(1, self.numWinnersRounds+1):
            if i == self.numWinnersRounds - 1 or i == self.numWinnersRounds:
                self.rounds.append(Round(i, self, 1, isWinners=True))
            else:
                self.rounds.append(Round(i, self, int(self.ceilPlayers/(2**i)), isWinners=True))

        for i in range(1, self.numLosersRounds+1):
            if i == 1:
                self.rounds.append(Round(i, self, int(self.rounds[0].numMatches/2), isWinners=False))
            elif i%2 == 0:
                self.rounds.append(Round(i, self, self.rounds[self.numLosersRounds + i-1].numMatches, isWinners=False))
            else:
                self.rounds.append(Round(i, self, int(
                    self.rounds[self.numLosersRounds + i-1].numMatches/2), isWinners=False))

        #for i in range(1, self.numWinnersRounds+1):
        #    self.rounds.append(Round(i, self, isWinners=True))
#        for i in range(1, self.numLosersRounds+1):
#            self.rounds.append(Round(i, self, isWinners=False))

        for i in range(0, len(self.rounds)):
            self.rounds[i].handleProgression()


class Round:
    def __init__(self, number, bracket, numMatches, isWinners):
        self.number = number
        self.bracket = bracket
        self.matches = []
        self.isWinners = isWinners
        self.numMatches = numMatches
        j = 0
        for i in range(0, self.numMatches):
            j+=1
            if number == 1 and isWinners == True:
                if (len(self.bracket.entrants) < self.bracket.ceilPlayers - i):
                    self.matches.append(Match(self.bracket.entrants[i], None, self, j))
                else:
                    self.matches.append(Match(self.bracket.entrants[i], self.bracket.entrants[self.bracket.ceilPlayers - i - 1], self, j))
            else:
                self.matches.append(Match(None, None, self, j))

    def post_to_db(self, bracket_model):
        # post the round object without the reference to the matches fk
        r_model = RoundModel(
            number=self.number,
            winners=self.isWinners,
            bracket=bracket_model
        )

        db.session.add(r_model); db.session.commit()

        # post all the round's matches  
        for match in self.matches:
            match.post_to_db(r_model)
        
        # post all the self references winner/loserPlaysInMatch
        # for match in self.matches:
        #     match.post_self_refs(r_model)

        # now reference all of the round's matches in matches foreign key 
        return


    def handleProgression(self):
        if (self.number == self.bracket.numWinnersRounds and 
            self.isWinners == True):
            return

        elif (self.number == self.bracket.numWinnersRounds - 1 and 
                self.isWinners == True):
            # TODO insert logic for grand finals reset
            return

        for i in range(0, len(self.matches)):

            if (self.isWinners == True):
                self.bracket.rounds[self.roundNumber].matches[int(math.floor(i/2))].setEntrant(self.matches[i].winner)
                # TODO implement double jeopardy avoidance (https://blog.smash.gg/changes-in-the-world-of-brackets-695ecb777a4c)
                if self.roundNumber == 1:
                    self.bracket.rounds[self.bracket.numWinnersRounds].matches[int(math.floor(i/2))].setEntrant(self.matches[i].loser) 
                else:
                    # should work, but no dj avoidance
                    self.bracket.rounds[self.bracket.numWinnersRounds + (self.roundNumber-1)*2 - 1].matches[i].setEntrant(self.matches[i].loser)
                    #placeInLosers += 2

            if (self.isWinners == False):
                ## place winner of losers finals in grand finals
                if self.roundNumber == self.bracket.numLosersRounds:
                    self.bracket.rounds[self.bracket.numWinnersRounds-2].matches[i].setEntrant(self.matches[i].winner)
                ##if next round has the same number of matches as the current round
                elif self.roundNumber%2 == 1:
                    self.bracket.rounds[self.bracket.numWinnersRounds + self.roundNumber].matches[i].setEntrant(self.matches[i].winner)
                ##if next round plays opponents from the winners bracket aka if next round in losers bracket has less matches than this round
                else:
                    self.bracket.rounds[self.bracket.numWinnersRounds + self.roundNumber].matches[int(math.floor(i/2))].setEntrant(self.matches[i].winner)

class Match:
    def __init__(self, entrant1, entrant2, matchRound, matchNumber):
        self.entrant1 = entrant1
        self.entrant2 = entrant2
        self.matchRound = matchRound
        self.matchNumber = matchNumber
        # Winner/loser/entrants put as lists because we need to copy the address of the list itself,
        # so when the winner of the match gets set, the match in which the winner plays in has it's entrant 
        # updated as well
        self.winner = [User("")]
        self.loser = [User("")]

    def post_to_db(self, round_model):
    
        u1_query = UserModel.query.filter_by(username=self.entrant1).first()
        u2_query = UserModel.query.filter_by(username=self.entrant2).first()

        u1_id = u1_query.id if u1_query is not None else None
        u2_id = u2_query.id if u2_query is not None else None
        r_id = round_model.id

        m_model = MatchModel(
            user_1 = u1_id,
            user_2 = u2_id,
            winner = None,
            round_id = r_id,
            # winner_advance_to = winner_match_id,
            # loser_advance_to = loser_match_id
        )

        db.session.add(m_model); db.session.commit()
        return

    def post_self_refs(self,):
        winner_match_id = None
        loser_match_id = None
        if type(self.winnerPlaysInMatch) == Match:
            w_query = MatchModel \
                        .query \
                        .filter_by(uuid=self.winnerPlaysInMatch.uuid) \
                        .first()


            if w_query is not None: winner_match_id = w_query.id 

        if type(self.loserPlaysInMatch) == Match:
            uuid = self.loserPlaysInMatch.uuid
            l_query = MatchModel \
                        .query \
                        .filter_by(uuid=uuid) \
                        .first()
            if l_query is not None: loser_match_id = l_query.id  

        match = MatchModel.query.filter_by(uuid=self.uuid).first()
        match.winner_advance_to = winner_match_id
        match.loser_advance_to = loser_match_id
        db.session.commit()

    #def winnerPlaysInMatch(self, nextMatch):
    #    self.winnerPlaysInMatch = nextMatch

    #def loserPlaysInMatch(self, nextMatch):
    #    self.loserPlaysInMatch = nextMatch

    def inputScore(self, scoreEntrant1, scoreEntrant2, winner, loser):
        ##TODO
        self.scoreEntrant1 = scoreEntrant1
        self.scoreEntrant2 = scoreEntrant2
        self.winner[0] = winner
        self.loser[0] = loser

    def entrantInMatch(self, entrant):
        if self.entrant1 == entrant:
            return True
        elif self.entrant2 == entrant:
            return True
        else:
            return False

    def setEntrant(self, entrant):
        if self.entrant1 == None:
            self.entrant1 = entrant
        elif self.entrant2 == None: 
            self.entrant2 = entrant
        elif self.entrant1[0] == None:
            self.entrant1[0] = entrant[0]
        elif self.entrant2[0] == None:
            self.entrant2[0] = entrant[0]
        else:
            if self.matchRound.isWinners:
                print("The winners round/match " + str(self.matchRound.roundNumber) + "/" + str(self.matchNumber) + " that user " + entrant[0].username + " is trying to be added to is full! Error")
            else:
                print("The losers round/match " + str(self.matchRound.roundNumber) + "/" + str(self.matchNumber) + " that user " + entrant[0].username + " is trying to be added to is full! Error")
