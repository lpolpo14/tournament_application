from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import TeamSerializer, PlayerSerializer, TeamMemberAddSerializer, TeamMemberSerializer
from .models import Team, Player


# Create your views here.

class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.prefetch_related('members__player').all() # Prefetch speeds up things a lot!
    search_fields = ["team_name", "sport_name"]
    ordering_fields = ["team_name", "sport_name", "created_at"]

    @action(detail=True, methods=["post"], url_path="add_player")
    def add_player(self, request, pk=None):
        team = self.get_object()

        serializer = TeamMemberAddSerializer(data=request.data, context={"team": team})

        serializer.is_valid(raise_exception=True)
        team_member = serializer.save()

        response_serializer = TeamMemberSerializer(team_member)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class PlayerViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    search_fields = ["name", "surname", "position"],
    ordering_fields = ["name", "surname", "main_shirt_number", "created_at"]


"""
class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.select_related('team', 'player').all() #Amazing time saver!
    # Instead of querying 3 times, we query once. Select_related returns the team and player objects as well!
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["team", "player", "shirt_number", "joined_at"]
    ordering = ["team", "shirt_number"]
    def get_serializer_class(self):
        if self.request.method in ["list", "retrieve"]:
            return TeamMemberSerializer
        return TeamMemberAddSerializer # for create
"""