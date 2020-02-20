from enum import Enum
from player import User
import math

class BracketTypes(Enum):
    DOUBLEELIMINATION = 1


class Tournament:
    def __init__(self, bracket):
        self.bracket = bracket

    ## expects an ordered list, where entry 0 of the list is the top seed and the last entry is the bottom seed
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
                self.rounds.append(Round(i, self, int(self.rounds[0].numMatches/2), isWinners=False))
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
class Round:
    def __init__(self, roundNumber, bracket, numMatches, isWinners):
        self.roundNumber = roundNumber
        self.bracket = bracket
        self.matches = []
        self.isWinners = isWinners
        self.numMatches = numMatches
        j = 0
        for i in range(0, self.numMatches):
            j+=1
            if roundNumber == 1 and isWinners == True:
                if (len(self.bracket.entrants) < self.bracket.ceilPlayers - i):
                    self.matches.append(Match(self.bracket.entrants[i], None, self, j))
                else:
                    self.matches.append(Match(self.bracket.entrants[i], self.bracket.entrants[self.bracket.ceilPlayers - i - 1], self, j))
            else:
                self.matches.append(Match(None, None, self, j))
    def handleProgression(self):
        if self.roundNumber == self.bracket.numWinnersRounds and self.isWinners == True:
            return
        elif self.roundNumber == self.bracket.numWinnersRounds-1 and self.isWinners == True:
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