from enum import Enum
from player import Entrant, Profile
import math

class BracketTypes(Enum):
    DOUBLEELIMINATION = 1  

 
class Tournament:
    def __init__(self, bracket):
        self.bracket = bracket
    def __init__(self, entrants, bracketType):
        self.bracket = Bracket(entrants, bracketType)

class Bracket:
    def __init__(self, entrants, bracketType):
        self.entrants = entrants
        self.bracketType = bracketType
        self.ceilPlayers = int(2**(math.ceil(math.log(len(self.entrants)))))
        if (bracketType == BracketTypes.DOUBLEELIMINATION):
            self.makeDoubleElimBracket()
            
    def makeDoubleElimBracket(self):
        # grand finals + reset round
        self.numWinnersRounds = int(math.log(self.ceilPlayers,2)+2) 
        self.numLosersRounds = int((math.log(self.ceilPlayers,2)) + math.log(math.log(self.ceilPlayers,2),2))
        self.numTotalRounds = self.numLosersRounds + self.numWinnersRounds
        self.rounds = []
        for i in range(1, self.numWinnersRounds+1):
            if i == self.numWinnersRounds - 1 or i == self.numWinnersRounds:
                self.rounds.append(Round(i, self, 1, isWinners=True))
            else: 
                self.rounds.append(Round(i, self, int(self.ceilPlayers/(2**i)), isWinners=True))

        for i in range(1, self.numLosersRounds+1):
            if i == 1:
                self.rounds.append(Round(i, self, int(self.ceilPlayers/(2**(2*(math.ceil(i/2))))), isWinners=False))
            elif i%2 == 0:
                self.rounds.append(Round(i, self, self.rounds[self.numLosersRounds + i-1].numMatches, isWinners=False))
            else:
                self.rounds.append(Round(i, self, int(self.rounds[self.numLosersRounds + i-1].numMatches/2), isWinners=False))

        #for i in range(1, self.numWinnersRounds+1):
        #    self.rounds.append(Round(i, self, isWinners=True))
#        for i in range(1, self.numLosersRounds+1):
#            self.rounds.append(Round(i, self, isWinners=False))

        for i in range(0, len(self.rounds)):
            self.rounds[i].handleProgression()
        print("nice")
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
                    self.matches.append(Match(self.bracket.entrants[i], None, self))
                else: 
                    self.matches.append(Match(self.bracket.entrants[i], self.bracket.entrants[self.bracket.ceilPlayers - i - 1], self))
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
                self.matches[i].winnerPlaysInMatch(self.bracket.rounds[self.roundNumber].matches[int(math.floor(i/2))])
                # TODO implement double jeopardy avoidance (https://blog.smash.gg/changes-in-the-world-of-brackets-695ecb777a4c)
                if self.roundNumber == 1:
                    self.matches[i].loserPlaysInMatch(self.bracket.rounds[self.bracket.numWinnersRounds].matches[int(math.floor(i/2))])
                else: 
                    # should work, but no dj avoidance 
                    self.matches[i].loserPlaysInMatch(self.bracket.rounds[self.bracket.numWinnersRounds + (self.roundNumber-1)*2 - 1].matches[i])
                    #placeInLosers += 2
            if (self.isWinners == False):
                ## place winner of losers finals in grand finals 
                if self.roundNumber == self.bracket.numLosersRounds:
                    self.matches[i].winnerPlaysInMatch(self.bracket.rounds[self.bracket.numWinnersRounds].matches[i])
                ##if next round has the same number of matches as the current round
                elif self.roundNumber%2 == 1:
                    self.matches[i].winnerPlaysInMatch(self.bracket.rounds[self.bracket.numWinnersRounds + self.roundNumber].matches[i])
                ##if next round plays opponents from the winners bracket aka if next round in losers bracket has less matches than this round 
                else:
                    self.matches[i].winnerPlaysInMatch(self.bracket.rounds[self.bracket.numWinnersRounds + self.roundNumber].matches[int(math.floor(i/2))])

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
            print("The match " + entrant.profile.tag + " is trying to proceed to is full! Error")