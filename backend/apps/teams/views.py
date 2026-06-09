from django.shortcuts import render
from rest_framework import viewsets

from .serializers import TeamSerializer
from .models import Team


# Create your views here.

class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    queryset = Team.objects.all()