from datetime import timedelta
from itertools import combinations
import random
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import TournamentParticipationSerializer
from ..teams.models import Team
from ..tournaments.models import Tournament, TournamentParticipation
from ..matches.models import Match, Stadium
from ..tournaments.serializers import TournamentSerializer
from .services import  calculate_tournament_standings
from ..users.permissions import IsTeamManager, IsSportsAdmin, DenyAll

from django.contrib.auth import get_user_model
from ..users.models import UserDetails

User = get_user_model()

"""
Right now we are using computed standings, meaning that we calculate standings constantly.
In the future it is suggested that we create a Standings model and save it there.
"""
class TournamentViewSet(viewsets.ModelViewSet):
    """
    The main tournament API Controller.
    """
    queryset = Tournament.objects.prefetch_related("teams", "participations__team").all()
    serializer_class = TournamentSerializer

    def get_permissions(self):
        """
        Only a team manager can request participation.
        Editing & Creation of the tournament can be achieved only by the Sports Administrator
        """
        if self.action in ["list", "retrieve", "standings"]:
            return [AllowAny()]

        if self.action == "request_registration":
            return [IsAuthenticated(), IsTeamManager()]

        if self.action in [
            "create",
            "registrations",
            "commence",
            "generate_matches",
            "complete",
            "cancel",
            "mark_ongoing",
        ]:
            return [IsAuthenticated(), IsSportsAdmin()]

        return [DenyAll()]



    @action(detail=True, methods=["post"], url_path="request-registration")
    def request_registration(self, request, pk=None):
        """
        An endpoint used by a team manager to request a registration to the tournament.
        It has a lot of self explainable checks.
        """
        tournament = self.get_object()

        if tournament.status != Tournament.Status.SCHEDULED:
            return Response(
                {"detail": "Teams can only register while tournament status is Scheduled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        team_id = request.data.get("team_id")

        if not team_id:
            return Response(
                {"team_id": "This field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        team = get_object_or_404(Team, pk=team_id)

        if team.manager_id != request.user.id:
            raise PermissionDenied(
                "You can only request tournament registration for your own team."
            )

        participation, created = TournamentParticipation.objects.get_or_create(
            tournament=tournament,
            team=team,
            defaults={"status": TournamentParticipation.Status.PENDING},
        )

        if not created:
            return Response(
                {"detail": f"This team already has a participation with status {participation.status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TournamentParticipationSerializer(participation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="registrations")
    def registrations(self, request, pk=None):
        """
        Used for viewing registrations for a tournament by an admin.
        """
        tournament = self.get_object()

        queryset = tournament.participations.select_related("team").order_by("-requested_at")

        participation_status = request.query_params.get("status")
        if participation_status: # This is optional. Not really used in the frontend.
            queryset = queryset.filter(status=participation_status)

        serializer = TournamentParticipationSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], name="commence")
    def commence(self, request, pk=None):
        """
        This endpoint officially starts a tournament.
        Before doing so - it checks for a lot of things. Everything is explained in the details
        field that is returned when a 400_BAD_REQUEST is made.
        """
        tournament = self.get_object()

        if tournament.status != Tournament.Status.SCHEDULED:
            return Response(
                {"details": "Only scheduled tournaments may commence."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tournament.teams.count() < 2:
            return Response(
                {"details": "Tournament must have at least 2 teams to commence."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not Stadium.objects.exists():
            return Response(
                {"detail": "At least one stadium is required before generating matches."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not User.objects.filter(details__role=UserDetails.Role.REFEREE).exists():
            return Response(
                {"detail": "At least one referee is required before generating matches."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tournament.status = Tournament.Status.ONGOING
        tournament.save()


        generated_matches = []

        # This field is very important. The sports_administrator can automatically generate matches
        # Without having to create a match one by one. Extremely useful if the admin wants
        # each team to play with every single other team.
        if request.data.get("generate_matches", True):
            generated_matches = self._generate_round_robin_matches(tournament)

        serializer = TournamentSerializer(tournament)

        return Response(
            {
                "detail": "Tournament commenced successfully.",
                "generated_matches": len(generated_matches),
                "tournament": serializer.data,
            }
        )

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        """
        Used for marking a tournament as complete.
        """
        tournament = self.get_object()

        matches = tournament.tournament_matches.all()

        if not matches.exists():
            return Response(
                {"detail": "Tournament cannot be completed because it has no matches."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        unfinished_matches = matches.exclude(
            match_status__in=[ # Neat!
                Match.Status.COMPLETED,
                Match.Status.CANCELLED,
            ]
        )

        if unfinished_matches.exists():
            return Response(
                {
                    "detail": "Tournament can only be completed when all matches are completed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        tournament.status = Tournament.Status.COMPLETED
        tournament.save(update_fields=["status"])

        serializer = TournamentSerializer(tournament)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """
        Used for cancelling a tournament. This is easily reversible (See next action).
        """
        tournament = self.get_object()

        if tournament.status == Tournament.Status.COMPLETED:
            return Response(
                {"detail": "Completed tournaments cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tournament.status = Tournament.Status.CANCELLED
        tournament.save(update_fields=["status"])

        serializer = TournamentSerializer(tournament)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="mark-ongoing")
    def mark_ongoing(self, request, pk=None):
        """
        Rollbacks the cancellation of a tournament.
        """
        tournament = self.get_object()

        if tournament.status != Tournament.Status.CANCELLED:
            return Response(
                {"detail": "Only cancelled tournaments can be marked as ongoing again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # This is a general rule we followed during implementation.
        if tournament.teams.count() < 2:
            return Response(
                {"detail": "Tournament must have at least two teams to be ongoing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tournament.status = Tournament.Status.ONGOING
        tournament.save(update_fields=["status"])

        serializer = TournamentSerializer(tournament)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="generate-matches")
    def generate_matches(self, request, pk=None):
        """
        A special endpoint used for the automatic generation of matches.
        It checks some important things before proceeding.
        """
        tournament = self.get_object()

        if tournament.status not in [Tournament.Status.SCHEDULED, Tournament.Status.ONGOING]:
            return Response(
                {"detail": "Matches can only be generated for ongoing or scheduled tournaments."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tournament.teams.count() < 2:
            return Response(
                {"detail": "At least two teams are required to generate matches."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not User.objects.filter(details__role=UserDetails.Role.REFEREE).exists():
            return Response(
                {"detail": "At least one referee is required before generating matches."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        generated_matches = self._generate_round_robin_matches(tournament)

        return Response(
            {
                "detail": "Generated matches successfully.",
                "generated_matches": len(generated_matches),
            }
        )

    def _generate_round_robin_matches(self, tournament):
        """
        Used for generating matches using the round-robin algorithm.
        A match is generated for every unique pair of teams.
        """
        # Regarding the stadiums and referees: The admin can change/edit these afterward - Practical.
        teams = list(tournament.teams.all())
        stadiums = list(Stadium.objects.all())
        pairs = list(combinations(teams, 2)) # Generates unique pairs
        # Only referees can be assigned to matches.
        referees = list(User.objects.filter(details__role=UserDetails.Role.REFEREE).order_by("id"))

        if not pairs:
            return []

        generated_matches = []

        total_tournament_seconds = (tournament.end_date - tournament.start_date).total_seconds()

        for index, (team1, team2) in enumerate(pairs):
            # Used to check for duplicates.
            reverse_exists = Match.objects.filter(
                tournament=tournament,
                team1=team2,
                team2=team1,
            ).exists()

            # Used to check for duplicates.
            normal_exists = Match.objects.filter(
                tournament=tournament,
                team1=team1,
                team2=team2,
            ).exists()

            if normal_exists or reverse_exists:
                continue

            # Spread matches evenly between the tournament start and finish times.
            if len(pairs) == 1: # Niche but nice.
                scheduled_date = tournament.start_date
            else:
                offset_seconds =  total_tournament_seconds * (index/ (len(pairs) -1))
                scheduled_date = tournament.start_date + timedelta(seconds=offset_seconds)

            stadium = random.choice(stadiums)
            referee = random.choice(referees)

            match = Match.objects.create(
                tournament=tournament,
                team1=team1,
                team2=team2,
                stadium=stadium,
                referee=referee,
                scheduled_date=scheduled_date,
                match_status=Match.Status.SCHEDULED,
            )
            generated_matches.append(match)
        return generated_matches

    @action(detail=True, methods=["get"], url_path="standings")
    def standings(self, request, pk=None):
        """
        Returns standings.
        """
        tournament = self.get_object()
        standings_list = calculate_tournament_standings(tournament)

        return Response(standings_list)


class TournamentParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Handles the registration requests. It is read only by default. Custom actions
    are able to write to the TournamentParticipation objects though.
    """
    queryset = TournamentParticipation.objects.select_related(
        "tournament",
        "team",
    ).all()

    serializer_class = TournamentParticipationSerializer
    permission_classes = [IsSportsAdmin] # Only SportsAdministrator uses this class.

    @action(detail=True, methods=["post"], url_path="accept")
    def accept(self, request, pk=None):
        registration = self.get_object()

        if registration.tournament.status != Tournament.Status.SCHEDULED:
            return Response(
                {"detail": "Registrations can only be accepted while the tournament is Scheduled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        registration.accept()

        serializer = self.get_serializer(registration)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        registration = self.get_object()

        if registration.tournament.status != Tournament.Status.SCHEDULED:
            return Response(
                {"detail": "Registrations can only be rejected while the tournament is Scheduled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        registration.reject()

        serializer = self.get_serializer(registration)
        return Response(serializer.data)