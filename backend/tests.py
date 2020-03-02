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

        self.assertTrue(tournament.bracket.rounds[0].matches[0].entrant1 == entrant1)
        self.assertTrue(tournament.bracket.rounds[0].matches[0].loserPlaysInMatch == tournament.bracket.rounds[0].matches[1].loserPlaysInMatch)
        self.assertTrue(tournament.bracket.rounds[0].matches[0].winnerPlaysInMatch == tournament.bracket.rounds[0].matches[1].winnerPlaysInMatch)
        self.assertTrue(tournament.bracket.rounds[5].matches[0].winnerPlaysInMatch == tournament.bracket.rounds[1].matches[0].loserPlaysInMatch)

if __name__ == '__main__':
    unittest.main()
