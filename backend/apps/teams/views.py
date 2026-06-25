from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .serializers import TeamSerializer, PlayerSerializer, addPlayerToTeamSerializer, TeamMemberSerializer
from .models import Team, Player, TeamMember


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

        return Response(status=status.HTTP_204_NO_CONTENT)

class PlayerViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    search_fields = ["name", "surname", "position"]
    ordering_fields = ["name", "surname", "main_shirt_number", "created_at"]
