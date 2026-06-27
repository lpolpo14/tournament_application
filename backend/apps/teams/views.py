from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .serializers import TeamSerializer, PlayerSerializer, addPlayerToTeamSerializer, TeamMemberSerializer
from .models import Team, Player, TeamMember
from ..matches.models import Match
from ..matches.serializers import MatchReadSerializer
from ..tournaments.services import calculate_tournament_standings
from ..tournaments.models import Tournament

# Create your views here.

class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.prefetch_related('members__player').all() # Prefetch speeds up things a lot!
    search_fields = ["team_name", "sport_name"]
    ordering_fields = ["team_name", "sport_name", "created_at"]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @action(detail=True, methods=["post"], url_path="add-player")
    def add_player(self, request, pk=None):
        team = self.get_object()

        serializer = addPlayerToTeamSerializer(data=request.data, context={"team": team})

        serializer.is_valid(raise_exception=True)
        team_member = serializer.save()

        response_serializer = TeamMemberSerializer(team_member)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["delete"],url_path=r"members/(?P<member_id>\d+)", # Sadly no Django Path Expression...
    )
    def remove_player(self, request, pk=None, member_id=None):
        team = self.get_object()

        try:
            team_member = TeamMember.objects.get(
                id=member_id,
                team=team,
            )
        except TeamMember.DoesNotExist:
            return Response(
                {"detail": "Player is not a member of this team."},
                status=status.HTTP_404_NOT_FOUND,
            )

        team_member.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)\

    @action(detail=True, methods=["get"], url_path="matches")
    def matches(self, request, pk=None):
        team = self.get_object()
        now = timezone.now()

        future_limit = int(request.query_params.get("future_limit", 3))
        future_limit = min(max(future_limit, 1), 10)

        team_matches = (
            Match.objects
            .select_related("tournament", "team1", "team2", "stadium")
            .filter(Q(team1=team) | Q(team2=team))
        )

        future_matches = (
            team_matches
            .filter(scheduled_date__gte=now)
            .exclude(match_status=Match.Status.CANCELLED)
            .order_by("scheduled_date")[:future_limit]
        )

        past_matches = (
            team_matches
            .filter(
                Q(match_status=Match.Status.COMPLETED) |
                Q(scheduled_date__lt=now)
            )
            .order_by("-scheduled_date")
        )

        return Response({
            "future_matches": MatchReadSerializer(future_matches, many=True).data,
            "past_matches": MatchReadSerializer(past_matches, many=True).data,
        })

    @action(detail=True, methods=["get"], url_path="tournament-standings")
    def tournament_standings(self, request, pk=None):
        team = self.get_object()

        tournaments = (Tournament.objects.prefetch_related("teams").filter(teams=team)
            .order_by("-start_date")
        )
        result = []
        for tournament in tournaments:
            standings = calculate_tournament_standings(tournament)

            team_standing = next(
                (   standing
                    for standing in standings
                    if standing["team_id"] == team.id
                ),
                None,
            )
            if not team_standing:
                continue

            result.append({
                "tournament_id": tournament.id,
                "tournament_name": tournament.name,
                "sport": tournament.sport,
                "location": tournament.location,
                "status": tournament.status,
                "start_date": tournament.start_date,
                "end_date": tournament.end_date,
                "team_standing": team_standing,
                "standings": standings,
            })

        return Response(result)

class PlayerViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    search_fields = ["name", "surname", "position"]
    ordering_fields = ["name", "surname", "main_shirt_number", "created_at"]
