from django.shortcuts import render
from rest_framework import viewsets, filters

from .serializers import TeamSerializer, PlayerSerializer, TeamMemberSerializer
from .models import Team, Player, TeamMember


# Create your views here.

class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.prefetch_related('members__player').all() # Prefetch speeds up things a lot!
    search_fields = ["team_name", "sport_name"]
    ordering_fields = ["team_name", "sport_name", "created_at"]

class PlayerViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    search_fields = ["name", "surname", "position"],
    ordering_fields = ["name", "surname", "main_shirt_number", "created_at"]

class TeamMemberViewSet(viewsets.ModelViewSet):
    serializer_class = TeamMemberSerializer
    queryset = TeamMember.objects.select_related('team', 'player').all() #Amazing time saver!
    # Instead of querying 3 times, we query once. Select_related returns the team and player objects as well!
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["team", "player", "shirt_number", "joined_at"]
    ordering = ["team", "shirt_number"]
