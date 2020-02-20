import unittest
from tournament import Tournament, Bracket, BracketTypes, Round, Match
from player import User

class TestBracketCreation(unittest.TestCase):
    
    def test_doubleElim(self):
        entrant1 = User("entrant1")
        entrant2 = User("entrant2")
        entrant3 = User("entrant3")
        entrant4 = User("entrant4")
        entrant5 = User("entrant5")
        entrant6 = User("entrant6")
        entrant7 = User("entrant7")
        entrant8 = User("entrant8")
        tournament = Tournament([entrant1, entrant2, entrant3, entrant4, entrant5, entrant6, entrant7, entrant8], BracketTypes.DOUBLEELIMINATION)

        for match in tournament.bracket.rounds[0].matches:
            match.inputScore(2, 1, match.entrant1 , match.entrant2)
        for round in tournament.bracket.rounds:
            for match in round.matches:
                if match.entrantInMatch(tournament.bracket.rounds[2].matches[0].loser):
                    print(str(round.roundNumber) + str(match.matchNumber))

        #for i in range(0, len(tournament.bracket.rounds)):
        #    tournament.bracket.rounds[i].handleProgression()
        self.assertTrue(tournament.bracket.rounds[0].matches[0].entrantInMatch(entrant1))
        self.assertTrue(tournament.bracket.rounds[0].matches[0].entrantInMatch(entrant8))
        self.assertTrue(tournament.bracket.rounds[1].matches[0].entrantInMatch(tournament.bracket.rounds[0].matches[0].winner))
        #self.assertTrue(tournament.bracket.rounds[0].matches[0].winnerPlaysInMatch == tournament.bracket.rounds[0].matches[1].winnerPlaysInMatch)
        self.assertTrue(tournament.bracket.rounds[5].matches[0].entrantInMatch(tournament.bracket.rounds[0].matches[0].loser))
        self.assertTrue(tournament.bracket.rounds[7].matches[0].entrantInMatch(tournament.bracket.rounds[6].matches[0].winner))
        self.assertTrue(tournament.bracket.rounds[8].matches[0].entrantInMatch(tournament.bracket.rounds[2].matches[0].loser))
        self.assertTrue(tournament.bracket.rounds[3].matches[0].entrantInMatch(tournament.bracket.rounds[8].matches[0].winner))

if __name__ == '__main__':
    unittest.main()
