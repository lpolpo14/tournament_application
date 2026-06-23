"""
Our first serializer! The following guide is amazing: https://github.com/fussionlab/VueJs-Django
"""
from rest_framework import serializers
from .models import Team, TeamMember, Player


class PlayerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = Player
        fields = ["id","name", "surname","full_name", "main_shirt_number", "position", "created_at"]
        read_only_fields = ["id", "full_name", "created_at"]

    def get_full_name(self, obj): # This is how we calculate variables based on the current object with Serializers!
        return f"{obj.name} {obj.surname}"


class TeamMemberSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    class Meta:
        model = TeamMember
        fields = ["id", "team", "player", "shirt_number", "joined_at"] # Change this later.
        read_only_fields = ["id", "joined_at"]

class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = ["id", "team_name", "sport_name", "members", "created_at"] # This is safer since we decide what can be viewed by VUE