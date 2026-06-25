from rest_framework import serializers

from ..matches.models import Match


class MatchReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ["id","tournament", "team1", "team2", "location", "team1_score", "team2_score", "scheduled_date", "match_status"]
        read_only_fields = ["id", "tournament", "team1", "team2", "location", "team1_score", "team2_score","scheduled_date" ,"match_status"]

class MatchWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ["tournament", "team1", "team2", "scheduled_date"]