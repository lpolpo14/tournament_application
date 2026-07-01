from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .serializers import TeamSerializer, PlayerSerializer, addPlayerToTeamSerializer, TeamMemberSerializer
from .models import Team, Player, TeamMember
from ..matches.models import Match, PlayerMatchStatistics
from ..matches.serializers import MatchReadSerializer
from ..tournaments.services import calculate_tournament_standings
from ..tournaments.models import Tournament
from ..users.permissions import IsTeamManager, DenyAll, IsTeamManagerOfTeam, is_team_manager


# Create your views here.

class TeamViewSet(viewsets.ModelViewSet):
    """
    Main API controller for teams.
    """
    serializer_class = TeamSerializer
    queryset = Team.objects.prefetch_related('members__player').all() # Prefetch speeds up things a lot!
    # Prefetch also avoids N+1 Queries.
    search_fields = ["team_name", "sport_name"]
    ordering_fields = ["team_name", "sport_name", "created_at"]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        """
        This method applies different permissions based on the endpoint action.
        Anyone can view the team.
        A team manager can create a team/
        A team manager of a specific team can update that team.
        """
        if self.action in [
            "list",
            "retrieve",
            "matches",
            "tournament_standings",
        ]:
            return [AllowAny()]

        if self.action == "mine":
            return [IsAuthenticated()]

        if self.action == "create":
            return [IsAuthenticated(), IsTeamManager()]

        if self.action in [
            "update",
            "partial_update",
            "destroy",
            "add_player",
            "remove_player",
        ]:
            return [IsAuthenticated(), IsTeamManagerOfTeam()]

        return [DenyAll()]

    def perform_create(self, serializer):
        """
        Automatically assigns the logged in user as the team manager during creation.
        """
        serializer.save(manager=self.request.user)

    @action(detail=True, methods=["post"], url_path="add-player")
    def add_player(self, request, pk=None):
        """
        Custom endpoint for adding a player to the team.
        """
        team = self.get_object()
        self.check_object_permissions(request, team) # Object-Level Permissions Check (Is TeamManager
        # Manager of that specific team?)

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
        """
        Custom endpoint for removing a player
        """
        team = self.get_object()

        self.check_object_permissions(request, team)
        # Check if player is indeed part of team.
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

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="matches")
    def matches(self, request, pk=None):
        """
        Returns the teams future and past matches.

        Future matches are limited for better display.
        """
        team = self.get_object()
        now = timezone.now()

        future_limit = int(request.query_params.get("future_limit", 3))
        future_limit = min(max(future_limit, 1), 10)

        team_matches = (
            Match.objects
            .select_related("tournament", "team1", "team2", "stadium")
            .filter(Q(team1=team) | Q(team2=team))
        )

        # Note - If a match is marked as Completed and schedule date has not yet been reached
        # in real life - the match will still show up.
        future_matches = (
            team_matches
            .filter(scheduled_date__gte=now)
            .exclude(match_status=Match.Status.CANCELLED)
            # .exclude(match_status=Match.Status.COMPLETED) Uncomment this to not include Completed matches.
            .order_by("scheduled_date")[:future_limit]
        )

        # Show completed matches or matches with schedule times past the current time (The moment the user
        # Clicks on this endpoint
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
        """
        Custom action for calculating the tournaments standings.

        For each tournament, the standings are calculated.
        """
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
            ) # Used for cleaner display.
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

    @action(detail=False, methods=["get"], url_path="mine")
    def mine(self, request):
        """
        Searches for a team manager's teams (If authenticated properly)
        """
        if not request.user.is_authenticated:
            return Response([], status=200)

        if not is_team_manager(request.user):
            return Response([], status=200)

        teams = (
            Team.objects
            .prefetch_related("members__player")
            .filter(manager=request.user)
            .order_by("team_name")
        )

        serializer = self.get_serializer(teams, many=True)
        return Response(serializer.data)

class PlayerViewSet(viewsets.ModelViewSet):
    """
    The Main Player View Set that handles player logic.
    """
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    search_fields = ["name", "surname", "position"]
    ordering_fields = ["name", "surname", "main_shirt_number", "created_at"]

    def get_permissions(self):
        """
        Anyone can view players and player statistics.

        Updating and deleting players is disabled.
        """
        if self.action in [
            "list",
            "retrieve",
            "statistics",
        ]:
            return [AllowAny()]

        if self.action == "create":
            return [IsAuthenticated(), IsTeamManager()]

        if self.action in [
            "update",
            "partial_update",
            "destroy",
        ]:
            return [DenyAll()]

        return [DenyAll()]

    @action(detail=True, methods=["get"], url_path="statistics")
    def statistics(self, request, pk=None):
        """
        Get all statistics for a specific player.
        """
        player = self.get_object()

        # Loads all statistics objects for a specific player.
        statistics = (
            PlayerMatchStatistics.objects
            .select_related(
                "match",
                "match__tournament",
                "match__team1",
                "match__team2",
                "match__stadium",
                "team",
                "player",
            )
            .filter(player=player)
            .order_by("-match__scheduled_date") # Order by most current match
        )

        completed_statistics = [
            statistic
            for statistic in statistics
            if statistic.match.match_status == Match.Status.COMPLETED
        ] # For completed matches.

        # Aggregated player totals.
        summary = {
            "played_matches": len(completed_statistics),
            "goals": sum(statistic.goals for statistic in completed_statistics),
            "fouls": sum(statistic.fouls for statistic in completed_statistics),
            "yellow_cards": sum(statistic.yellow_cards for statistic in completed_statistics),
            "red_cards": sum(statistic.red_cards for statistic in completed_statistics),
        }

        match_history = []

        # Per match statistics.
        for statistic in statistics:
            match = statistic.match

            # Calculate team for the specific player
            if statistic.team_id == match.team1_id:
                opponent = match.team2
                player_team_score = match.team1_score
                opponent_score = match.team2_score
            else:
                opponent = match.team1
                player_team_score = match.team2_score
                opponent_score = match.team1_score
            result = "Not completed"

            # Calculate match result based on the player's team.
            if (
                    match.match_status == Match.Status.COMPLETED
                    and player_team_score is not None
                    and opponent_score is not None
            ):
                if player_team_score > opponent_score:
                    result = "Win"
                elif player_team_score < opponent_score:
                    result = "Loss"
                else:
                    result = "Draw"

            match_history.append({
                "match_id": match.id,
                "tournament_id": match.tournament.id,
                "tournament_name": match.tournament.name,
                "team_id": statistic.team.id,
                "team_name": statistic.team.team_name,
                "opponent_id": opponent.id,
                "opponent_name": opponent.team_name,
                "scheduled_date": match.scheduled_date,
                "stadium_name": match.stadium.name if match.stadium else None,
                "stadium_city": match.stadium.city if match.stadium else None,
                "match_status": match.match_status,
                "team_score": player_team_score,
                "opponent_score": opponent_score,
                "result": result,
                "goals": statistic.goals,
                "fouls": statistic.fouls,
                "yellow_cards": statistic.yellow_cards,
                "red_cards": statistic.red_cards,
                "extra_statistics": statistic.extra_statistics,
            })

        return Response({
            "player": PlayerSerializer(player).data,
            "summary": summary,
            "match_history": match_history,
        })
