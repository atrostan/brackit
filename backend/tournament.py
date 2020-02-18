from enum import Enum
from player import User
from app import db
import math

from app.models import Tournament as TournamentModel
from app.models import Bracket as BracketModel
from app.models import Match as MatchModel
from app.models import Round as RoundModel
from app.models import User as UserModel

class BracketTypes(Enum):
    DOUBLE_ELIMINATION = 1


class Tournament:
    def __init__(self, bracket):
        self.bracket = bracket

    # expects an ordered list, where entry 0 of the list is the top seed and
    # the last entry is the bottom seed
    def __init__(self, entrants, bracketType):

        # convert a list of tuples (competitor name, seed) to an ordered
        # list to be consumed by Bracket constructor
        if len(entrants) > 0:
            if type(entrants[0]) == tuple:
                entrants = [t[0] for t in sorted(entrants, key=lambda x: x[1])]

        self.bracket = Bracket(entrants, bracketType)

    def push_to_db(self, t_name, TO):
        """push tournament to db
        
        Arguments:
            t_name {string} -- tournament name
            TO {string} -- name of tournament organizer
        """
        # tournament organizer id
        o_id = UserModel.query.filter_by(username=TO).first_or_404().id

        t_model = TournamentModel(
            n_entrants = len(self.bracket.entrants),
            name = t_name,
            organizer_id = o_id
        )

        db.session.add(t_model)
        db.session.commit()
        return


class Bracket:
    def __init__(self, entrants, bracketType):
        self.entrants = entrants
        self.bracketType = bracketType
        self.ceilPlayers = int(2**(math.ceil(math.log(len(self.entrants)))))
        if (bracketType == BracketTypes.DOUBLE_ELIMINATION):
            self.makeDoubleElimBracket()

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
                self.rounds.append(Round(i, self, int(self.ceilPlayers/(2**i)),
                                         isWinners=True))

        for i in range(1, self.numLosersRounds+1):
            if i == 1:
                self.rounds.append(Round(i, self, int(
                    self.ceilPlayers/(2**(2*(math.ceil(i/2))))), isWinners=False))
            elif i % 2 == 0:
                self.rounds.append(Round(
                    i, self, self.rounds[self.numLosersRounds + i-1].numMatches, isWinners=False))
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
    def __init__(self, roundNumber, bracket, numMatches, isWinners):
        self.roundNumber = roundNumber
        self.bracket = bracket
        self.matches = []
        self.isWinners = isWinners
        self.numMatches = numMatches
        for i in range(0, self.numMatches):
            if roundNumber == 1 and isWinners == True:
                if (len(self.bracket.entrants) < self.bracket.ceilPlayers - i):
                    self.matches.append(
                        Match(self.bracket.entrants[i], None, self))
                else:
                    self.matches.append(Match(
                        self.bracket.entrants[i], self.bracket.entrants[self.bracket.ceilPlayers - i - 1], self))
            else:
                self.matches.append(Match(None, None, self))

    def handleProgression(self):
        if self.roundNumber == self.bracket.numWinnersRounds and self.isWinners == True:
            return
        elif self.roundNumber == self.bracket.numWinnersRounds-1 and self.isWinners == True:
            # TODO insert logic for grand finals reset
            return
        for i in range(0, len(self.matches)):
            if (self.isWinners == True):
                self.matches[i].winnerPlaysInMatch(
                    self.bracket.rounds[self.roundNumber].matches[int(math.floor(i/2))])
                # TODO implement double jeopardy avoidance (https://blog.smash.gg/changes-in-the-world-of-brackets-695ecb777a4c)
                if self.roundNumber == 1:
                    self.matches[i].loserPlaysInMatch(
                        self.bracket.rounds[self.bracket.numWinnersRounds].matches[int(math.floor(i/2))])
                else:
                    # should work, but no dj avoidance
                    self.matches[i].loserPlaysInMatch(
                        self.bracket.rounds[self.bracket.numWinnersRounds + (self.roundNumber-1)*2 - 1].matches[i])
                    #placeInLosers += 2
            if (self.isWinners == False):
                ## place winner of losers finals in grand finals
                if self.roundNumber == self.bracket.numLosersRounds:
                    self.matches[i].winnerPlaysInMatch(
                        self.bracket.rounds[self.bracket.numWinnersRounds].matches[i])
                ##if next round has the same number of matches as the current round
                elif self.roundNumber % 2 == 1:
                    self.matches[i].winnerPlaysInMatch(
                        self.bracket.rounds[self.bracket.numWinnersRounds + self.roundNumber].matches[i])
                ##if next round plays opponents from the winners bracket aka if next round in losers bracket has less matches than this round
                else:
                    self.matches[i].winnerPlaysInMatch(
                        self.bracket.rounds[self.bracket.numWinnersRounds + self.roundNumber].matches[int(math.floor(i/2))])


class Match:
    def __init__(self, entrant1, entrant2, matchRound):
        self.entrant1 = entrant1
        self.entrant2 = entrant2
        self.matchRound = matchRound

    def winnerPlaysInMatch(self, nextMatch):
        self.winnerPlaysInMatch = nextMatch

    def loserPlaysInMatch(self, nextMatch):
        self.loserPlaysInMatch = nextMatch

    def inputScore(self, scoreEntrant1, scoreEntrant2, winner, loser):
        ##TODO
        self.scoreEntrant1 = scoreEntrant1
        self.scoreEntrant2 = scoreEntrant2
        self.winner = winner
        self.proceedToMatch(winner, self.winnerPlaysInMatch)
        self.proceedToMatch(loser, self.loserPlaysInMatch)

    def proceedToMatch(self, entrant, match):
        if match.entrant1 == None:
            match.entrant1 = entrant
        elif match.entrant2 == None:
            match.entrant2 = entrant
        else:
            print("The match " + entrant.profile.tag +
                  " is trying to proceed to is full! Error")
