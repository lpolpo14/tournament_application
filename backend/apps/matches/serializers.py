from rest_framework import serializers

from ..matches.models import Match


class MatchReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ["id","tournament", "team1", "team2", "team1_score", "team2_score", "location", "scheduled_date", "match_status"]
        read_only_fields = ["id", "tournament", "team1", "team2", "team1_score", "team2_score", "location", "scheduled_date" ,"match_status"]

class MatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ["tournament", "team1", "team2", "location", "scheduled_date"]

    def validate(self, attrs):
        team1 = attrs.get("team1")
        team2 = attrs.get("team2")
        tournament = attrs.get("tournament")

        if team1 == team2:
            raise serializers.ValidationError("A team can't play against itself")

        if not tournament.teams.filter(id=team1.id).exists():
            raise serializers.ValidationError("The team is not assigned to the tournament")

        if not tournament.teams.filter(id=team2.id).exists():
            raise serializers.ValidationError("The team is not assigned to the tournament")

        return attrs

class MatchPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ["team1_score", "team2_score", "match_status"]

    def validate(self, attrs):
        team1_score = attrs.get(
            "team1_score",
            self.instance.team1_score if self.instance else None
        )

        team2_score = attrs.get(
            "team2_score",
            self.instance.team2_score if self.instance else None
        )

        match_status = attrs.get(
            "match_status",
            self.instance.match_status if self.instance else None
        )

        if team1_score is None and team2_score is None:
            raise serializers.ValidationError("You must provide both scores")

        if team1_score is not None and team2_score is None:
            raise serializers.ValidationError("You must provide both scores")

        if team1_score is None and team2_score is not None:
            raise serializers.ValidationError("You must provide both scores")

        return attrs