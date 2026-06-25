from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..tournaments.models import Tournament
from ..matches.models import Match
from ..tournaments.serializers import TournamentSerializer

# Create your views here.

"""
Right now we are using computed standings, meaning that we calculate standings constantly.
In the future it is suggested that we create a Standings model and save it there.
"""
class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.prefetch_related("teams").all()
    serializer_class = TournamentSerializer

    @action(detail=True, methods=['get'], url_path='standings')
    def standings(self, request, pk=None):
        tournament = self.get_object()

        standings = {}
        for team in tournament.teams.all():
            standings[team.id] = {
                'team_id': team.id,
                "team_name": team.name,
                "played_games": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "goals_scored": 0,
                "goals_conceded": 0,
                "points": 0,
            }

        completed_matches = (Match.objects.select_related("team1","team2")
                             .filter(tournament=tournament, match_status="Completed"))
        for match in completed_matches:
            team1 = match.team1
            team2 = match.team2
            if team1.id not in standings or team2.id not in standings:
                continue

            team1_standing = standings[team1.id]
            team2_standing = standings[team2.id]

            team1_score = match.team1_score
            team2_score = match.team2_score

            team1_standing['played_games'] += 1
            team2_standing['played_games'] += 1

            team1_standing["goals_scored"] += team1_score
            team1_standing["goals_conceded"] += team2_score

            team2_standing["goals_scored"] += team2_score
            team2_standing["goals_conceded"] += team1_score

            # We will see regarding points later.
            if team1_score > team2_score:
                team1_standing["wins"] += 1
                team2_standing["losses"] += 1
                team1_standing["points"] += 3
            elif team1_score < team2_score:
                team2_standing["wins"] += 1
                team1_standing["losses"] += 1
                team2_standing["points"] += 3
            else:
                team1_standing["draws"] += 1
                team2_standing["draws"] += 1
                team1_standing["points"] += 1
                team2_standing["points"] += 1

        standings_list = list(standings.values())

        standings_list.sort(key=lambda x: -x["points"])

        for index, team_entry in enumerate(standings_list, start=1):
            team_entry["position"] = index

        return Response(standings_list)