from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import MatchPatchSerializer
from ..matches.serializers import (MatchReadSerializer, MatchCreateSerializer,
                                   MatchPatchSerializer, StadiumSerializer)
from ..matches.models import Match, Stadium

# Create your views here.

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.select_related("tournament","team1","team2").all()
    search_fields = ["tournament", "team1", "team2", "location"]
    ordering_fields = ["scheduled_date"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return MatchReadSerializer
        if self.action == "create":
            return MatchCreateSerializer
        return MatchPatchSerializer

    def get_queryset(self):
        queryset = Match.objects.select_related(
            "tournament",
            "team1",
            "team2",
        ).all()

        tournament_id = self.request.query_params.get("tournament")

        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)

        return queryset
    """
    def get_queryset(self):
        queryset = super().get_queryset()

        tournament_id = self.request.query_params.get("tournament")
        team_id = self.request.query_params.get("team")

        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)

        if team_id:
            queryset = queryset.filter(
                Q(team1_id=team_id) | Q(team2_id=team_id)
            ) # This is a bit obtuse. Fix it soon.

        return queryset
    """

    @action(detail=True, methods=["patch"], url_path="submit-score")
    def submit_score(self, request, pk=None):
        match = self.get_object()

        serializer = MatchPatchSerializer(match, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        updated_match = serializer.save(match_status="Completed")

        read_serializer = MatchReadSerializer(updated_match)
        return Response(read_serializer.data)

class StadiumViewSet(viewsets.ModelViewSet):
    queryset = Stadium.objects.all().order_by("name")
    serializer_class = StadiumSerializer