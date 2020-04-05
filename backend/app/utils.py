from app.models import Tournament as TournamentModel
from app.models import Bracket as BracketModel
from app.models import Match as MatchModel
from app.models import Round as RoundModel
from app.models import User as UserModel

def get_to(m_id):
    match = MatchModel.query.filter_by(id=m_id).first_or_404()
    r_id = match.round_id
    round = RoundModel.query.filter_by(id=r_id).first_or_404()
    b_id = round.bracket_id
    bracket = BracketModel.query.filter_by(id=b_id).first_or_404()
    t_id = bracket.tournament_id
    tournament = TournamentModel.query.filter_by(id=t_id).first_or_404()
    return tournament.organizer_id
