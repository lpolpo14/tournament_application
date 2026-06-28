from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..users.models import UserDetails
from ..matches.models import Match, Stadium, PlayerMatchStatistics
from ..teams.models import TeamMember

User = get_user_model()


class MatchReadSerializer(serializers.ModelSerializer):
    team1_name = serializers.CharField(source="team1.team_name", read_only=True)
    team2_name = serializers.CharField(source="team2.team_name", read_only=True)
    tournament_name = serializers.CharField(source="tournament.name", read_only=True)
    player_statistics_count = serializers.IntegerField(source="player_statistics.count", read_only=True)

    stadium_name = serializers.CharField(source="stadium.name", read_only=True)
    stadium_city = serializers.CharField(source="stadium.city", read_only=True)

    referee_username = serializers.CharField(source="referee.username", read_only=True)

    class Meta:
        model = Match
        fields = [
            "id",
            "tournament",
            "tournament_name",
            "team1",
            "team1_name",
            "team2",
            "team2_name",
            "player_statistics_count",
            "stadium",
            "stadium_name",
            "stadium_city",
            "referee",
            "referee_username",
            "team1_score",
            "team2_score",
            "scheduled_date",
            "match_status",
        ]

        read_only_fields = fields

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

class MatchCreateSerializer(serializers.ModelSerializer):
    referee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(details__role=UserDetails.Role.REFEREE),
        required=True,
    )

    class Meta:
        model = Match
        fields = [
            "tournament",
            "team1",
            "team2",
            "stadium",
            "referee",
            "scheduled_date",
        ]

    def validate(self, attrs):
        team1 = attrs.get("team1")
        team2 = attrs.get("team2")
        tournament = attrs.get("tournament")

        if team1 == team2:
            raise serializers.ValidationError("A team cannot play against itself.")

        if not tournament.teams.filter(id=team1.id).exists():
            raise serializers.ValidationError("Team 1 is not assigned to the tournament.")

        if not tournament.teams.filter(id=team2.id).exists():
            raise serializers.ValidationError("Team 2 is not assigned to the tournament.")

        return attrs

class StadiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stadium
        fields = [
            "id",
            "name",
            "city",
            "address",
        ]

class PlayerMatchStatisticsSerializer(serializers.ModelSerializer):
    player_full_name = serializers.SerializerMethodField()
    team_name = serializers.CharField(source="team.team_name", read_only=True)
    shirt_number = serializers.SerializerMethodField()

    class Meta:
        model = PlayerMatchStatistics
        fields = [
            "id", "match", "player", "player_full_name", "team", "team_name","shirt_number",
            "goals", "fouls", "yellow_cards", "red_cards", "extra_statistics", "created_at",
            "updated_at",
        ]

        read_only_fields = [ "id", "player_full_name", "team_name", "shirt_number", "created_at",
            "updated_at", ]

    def get_player_full_name(self, obj):
        return f"{obj.player.name} {obj.player.surname}"

    def get_shirt_number(self, obj):
        membership = TeamMember.objects.filter(
            team=obj.team,
            player=obj.player,
        ).first()

        if not membership:
            return None

        return membership.shirt_number

    def validate(self, attrs):
        match = attrs.get("match", self.instance.match if self.instance else None)
        team = attrs.get("team", self.instance.team if self.instance else None)
        player = attrs.get("player", self.instance.player if self.instance else None)

        if not match:
            raise serializers.ValidationError("Match is required.")

        if not team:
            raise serializers.ValidationError("Team is required.")

        if not player:
            raise serializers.ValidationError("Player is required.")

        if team not in [match.team1, match.team2]:
            raise serializers.ValidationError(
                "The selected team does not participate in this match."
            )

        if not TeamMember.objects.filter(team=team, player=player).exists():
            raise serializers.ValidationError(
                "The selected player does not belong to the selected team."
            )

        return attrs