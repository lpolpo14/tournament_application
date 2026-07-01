from rest_framework import serializers

from ..teams.models import Team
from ..teams.serializers import TeamSerializer
from ..tournaments.models import Tournament, TournamentParticipation

class TournamentSerializer(serializers.ModelSerializer):
    """
    Main tournament serializer. Returns full team information. It accepts Team IDs for writing.
    """
    # Read-only nested Team data when displaying tournament details.
    teams = TeamSerializer(many=True, read_only=True)

    # Write only fields that allows the API to receive team IDs when creating/updating the tournament.
    teams_ids = serializers.PrimaryKeyRelatedField(
        source="teams", queryset=Team.objects.all(), many=True, write_only=True, required=False
    )

    # Computed field (See function)
    pending_registration_count = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = ["id", "name", "sport", "teams", "teams_ids",
                  "location", "start_date", "end_date", "status", "pending_registration_count"]

    def get_pending_registration_count(self, obj):
        return obj.participations.filter(
            status=TournamentParticipation.Status.PENDING,
        ).count()


class TournamentParticipationSerializer(serializers.ModelSerializer):
    """
    Serializer for tournament participation requests.
    """
    team_name = serializers.SerializerMethodField()
    tournament_name = serializers.CharField(source="tournament.name", read_only=True)
    class Meta:
        model = TournamentParticipation
        fields = ["id", "tournament", "tournament_name", "team", "team_name",
                  "status", "requested_at", "request_answered_at"]

    def get_team_name(self, obj):
        return getattr(obj.team, "team_name", str(obj.team)) #safer with fallback.
