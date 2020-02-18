import unittest
from tournament import Tournament, Bracket, BracketTypes, Round, Match
from player import Entrant, Profile

class TestBracketCreation(unittest.TestCase):
    def test_doubleElim(self):
        entrant1 = Entrant("entrant1", 1)
        entrant2 = Entrant("entrant2", 2)
        entrant3 = Entrant("entrant3", 3)
        entrant4 = Entrant("entrant4", 4)
        entrant5 = Entrant("entrant5", 5)
        entrant6 = Entrant("entrant6", 6)
        entrant7 = Entrant("entrant7", 7)
        entrant8 = Entrant("entrant8", 8)
        tournament = Tournament([entrant1, entrant2, entrant3, entrant4, entrant5, entrant6, entrant7, entrant8], BracketTypes.DOUBLEELIMINATION)

        self.assertTrue(tournament.bracket.rounds[0].matches[0].entrant1 == entrant1)
        self.assertTrue(tournament.bracket.rounds[0].matches[0].loserPlaysInMatch == tournament.bracket.rounds[0].matches[1].loserPlaysInMatch)
        self.assertTrue(tournament.bracket.rounds[0].matches[0].winnerPlaysInMatch == tournament.bracket.rounds[0].matches[1].winnerPlaysInMatch)
        self.assertTrue(tournament.bracket.rounds[5].matches[0].winnerPlaysInMatch == tournament.bracket.rounds[1].matches[0].loserPlaysInMatch)

if __name__ == '__main__':
    unittest.main()
