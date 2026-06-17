"""
Our first serializer! The following guide is amazing: https://github.com/fussionlab/VueJs-Django
"""
from rest_framework import serializers
from .models import Team, TeamMember


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "team_name", "sport_name"] # This is safer since we decide what can be viewed by VUE

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__' # Change this later.