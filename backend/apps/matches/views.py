from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import MatchPatchSerializer
from ..matches.serializers import (MatchReadSerializer, MatchCreateSerializer,
                                   MatchPatchSerializer, StadiumSerializer, MatchAdminUpdateSerializer)
from ..matches.models import Match, Stadium
from ..teams.models import TeamMember
from ..users.permissions import  IsSportsAdmin, \
    IsReferee, IsAssignedReferee, DenyAll, CanEditPlayerMatchStatistics


# Create your views here.

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.select_related(
        "tournament",
        "team1",
        "team2",
        "stadium",
        "referee",
    ).all()
    search_fields = ["tournament", "team1", "team2", "location"]
    ordering_fields = ["scheduled_date"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "players"]:
            return MatchReadSerializer

        if self.action == "create":
            return MatchCreateSerializer

        if self.action == "admin_update":
            return MatchAdminUpdateSerializer

        return MatchPatchSerializer

    def get_queryset(self):
        queryset = Match.objects.select_related(
            "tournament",
            "team1",
            "team2",
            "stadium",
            "referee",
        ).all()

        tournament_id = self.request.query_params.get("tournament")

        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)

        return queryset

    def get_permissions(self):
        if self.action in ["list", "retrieve", "players"]:
            return [AllowAny()]

        if self.action == "assigned_to_me":
            return [IsAuthenticated(), IsReferee()]

        if self.action in ["create", "admin_update", "cancel"]:
            return [IsAuthenticated(), IsSportsAdmin()]

        if self.action == "submit_score":
            return [IsAuthenticated(), IsReferee(), IsAssignedReferee()]

        return [DenyAll()]

    @action(detail=False, methods=["get"], url_path="assigned-to-me")
    def assigned_to_me(self, request):
        matches = (
            Match.objects
            .select_related(
                "tournament",
                "team1",
                "team2",
                "stadium",
                "referee",
            )
            .filter(referee=request.user)
            .exclude(match_status=Match.Status.COMPLETED)
            .exclude(match_status=Match.Status.CANCELLED)
            .order_by("scheduled_date")
        )

        serializer = MatchReadSerializer(matches, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="admin-update")
    def admin_update(self, request, pk=None):
        match = self.get_object()

        serializer = MatchAdminUpdateSerializer(
            match,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        updated_match = serializer.save()

        read_serializer = MatchReadSerializer(updated_match)
        return Response(read_serializer.data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        match = self.get_object()

        if match.match_status == Match.Status.COMPLETED:
            return Response(
                {"detail": "Completed matches cannot be cancelled."},
                status=400,
            )

        match.match_status = Match.Status.CANCELLED
        match.save(update_fields=["match_status"])

        serializer = MatchReadSerializer(match)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="players")
    def players(self, request, pk=None):
        match = self.get_object()

        def serialize_members(team):
            members = (TeamMember.objects.select_related("player")
                       .filter(team=team).order_by("shirt_number")
            )

            return [
                {
                    "team_member_id": member.id,
                    "player_id": member.player.id,
                    "player_name": member.player.name,
                    "player_surname": member.player.surname,
                    "player_full_name": f"{member.player.name} {member.player.surname}",
                    "shirt_number": member.shirt_number,
                    "position": member.player.position,
                }
                for member in members
            ]

        return Response(
            {
                "team1": {
                    "id": match.team1.id,
                    "team_name": match.team1.team_name,
                    "players": serialize_members(match.team1),
                },
                "team2": {
                    "id": match.team2.id,
                    "team_name": match.team2.team_name,
                    "players": serialize_members(match.team2),
                },
            }
        )

    @action(detail=True, methods=["patch"], url_path="submit-score")
    def submit_score(self, request, pk=None):
        match = self.get_object()

        self.check_object_permissions(request, match) # Amazing function!

        serializer = MatchPatchSerializer(match, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        updated_match = serializer.save(match_status="Completed")

        read_serializer = MatchReadSerializer(updated_match)
        return Response(read_serializer.data)

class StadiumViewSet(viewsets.ModelViewSet):
    queryset = Stadium.objects.all().order_by("name")
    serializer_class = StadiumSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        if self.action == "create":
            return [IsAuthenticated(), IsSportsAdmin()]

        # Block else.
        return [DenyAll()]

from ..matches.models import Match, Stadium, PlayerMatchStatistics
from ..matches.serializers import (
    MatchReadSerializer,
    MatchCreateSerializer,
    MatchPatchSerializer,
    StadiumSerializer,
    PlayerMatchStatisticsSerializer,
)

class PlayerMatchStatisticsViewSet(viewsets.ModelViewSet):
    queryset = PlayerMatchStatistics.objects.select_related(
        "match","player","team","match__team1","match__team2",
    ).all()
    serializer_class = PlayerMatchStatisticsSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        return [IsAuthenticated(), CanEditPlayerMatchStatistics()]

    def get_queryset(self):
        queryset = super().get_queryset()
        match_id = self.request.query_params.get("match")
        team_id = self.request.query_params.get("team")
        player_id = self.request.query_params.get("player")

        if match_id:
            queryset = queryset.filter(match_id=match_id)
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        if player_id:
            queryset = queryset.filter(player_id=player_id)
        return queryset

    def perform_create(self, serializer):
        match = serializer.validated_data["match"]

        if match.referee_id != self.request.user.id:
            raise PermissionDenied(
                "You can only add statistics for matches assigned to you."
            )

        serializer.save(referee=self.request.user)

    def perform_update(self, serializer):
        statistic = self.get_object()
        self.check_object_permissions(self.request, statistic)
        serializer.save(referee=self.request.user)

    def perform_destroy(self, instance):
        self.check_object_permissions(self.request, instance)
        instance.delete()