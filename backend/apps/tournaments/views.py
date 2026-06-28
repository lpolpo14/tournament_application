from datetime import timedelta
from itertools import combinations
from random import random

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

# Create your views here.

"""
Right now we are using computed standings, meaning that we calculate standings constantly.
In the future it is suggested that we create a Standings model and save it there.
"""
class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.prefetch_related("teams", "participations__team").all()
    serializer_class = TournamentSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "standings"]:
            return [AllowAny()]

        if self.action == "request_registration":
            return [IsAuthenticated(), IsTeamManager()]

        if self.action in [
            "create",
            "registrations",
            "commence",
            "generate_matches",
        ]:
            return [IsAuthenticated(), IsSportsAdmin()]

        return [DenyAll()]

    @action(detail=True, methods=["post"], url_path="request-registration")
    def request_registration(self, request, pk=None):
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
        tournament = self.get_object()

        queryset = tournament.participations.select_related("team").order_by("-requested_at")

        participation_status = request.query_params.get("status")
        if participation_status:
            queryset = queryset.filter(status=participation_status)

        serializer = TournamentParticipationSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], name="commence")
    def commence(self, request, pk=None):
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

        tournament.status = Tournament.Status.ONGOING
        tournament.save()


        generated_matches = []

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

    @action(detail=True, methods=["post"], url_path="generate-matches")
    def generate_matches(self, request, pk=None):
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

        generated_matches = self._generate_round_robin_matches(tournament)

        return Response(
            {
                "detail": "Generated matches successfully.",
                "generated_matches": len(generated_matches),
            }
        )

    def _generate_round_robin_matches(self, tournament):
        teams = list(tournament.teams.all())
        stadiums = list(Stadium.objects.all())
        pairs = list(combinations(teams, 2))

        if not pairs:
            return []

        generated_matches = []

        total_tournament_seconds = (tournament.end_date - tournament.start_date).total_seconds()

        for index, (team1, team2) in enumerate(pairs):
            reverse_exists = Match.objects.filter(
                tournament=tournament,
                team1=team2,
                team2=team1,
            ).exists()

            normal_exists = Match.objects.filter(
                tournament=tournament,
                team1=team1,
                team2=team2,
            ).exists()

            if normal_exists or reverse_exists:
                continue

            if len(pairs) == 1:
                scheduled_date = tournament.start_date
            else:
                offset_seconds =  total_tournament_seconds * (index/ (len(pairs) -1))
                scheduled_date = tournament.start_date + timedelta(seconds=offset_seconds)

            stadium = random.choice(stadiums)

            match = Match.objects.create(
                tournament=tournament,
                team1=team1,
                team2=team2,
                stadium=stadium,
                scheduled_date=scheduled_date,
                location=tournament.location,
                match_status=Match.Status.SCHEDULED,
            )
            generated_matches.append(match)
        return generated_matches

    @action(detail=True, methods=["get"], url_path="standings")
    def standings(self, request, pk=None):
        tournament = self.get_object()
        standings_list = calculate_tournament_standings(tournament)

        return Response(standings_list)


class TournamentParticipationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TournamentParticipation.objects.select_related(
        "tournament",
        "team",
    ).all()

    serializer_class = TournamentParticipationSerializer
    permission_classes = [IsSportsAdmin]

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