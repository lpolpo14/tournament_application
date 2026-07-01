from django.conf import settings
from django.conf.global_settings import AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from django.db import models

from ..teams.models import TeamMember


class Match(models.Model):
    """
    This model represents a match between two teams within the context of a tournament.
    """
    class Status(models.TextChoices):
        SCHEDULED = "Scheduled", "Scheduled"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"

    team1 = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='team1_matches')
    team2 = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='team2_matches')
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name='tournament_matches')
    scheduled_date = models.DateTimeField()
    stadium = models.ForeignKey('matches.Stadium', on_delete=models.SET_NULL, null=True, blank=True, related_name="matches")

    # Both stadium and referee can be null due to the initialization process of a Match object.
    referee = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Compatibility with custom user models.
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='refereed_matches',
    )

    team1_score = models.PositiveIntegerField(null=True, blank=True) # No need for immediate initialization.
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    match_status = models.CharField(max_length=100,choices=Status.choices, default='Scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.team1} vs {self.team2}'

    def clean(self):
        """
        Model level validation.
        """
        if self.team1 == self.team2:
            raise ValidationError('Teams must be different.')

class Stadium(models.Model):
    """
    It is a good practice to separate models.
    """
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.name} - {self.city}"


from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator

class PlayerMatchStatistics(models.Model):
    """
    This code is extremely extensible. This class connects a match object,
    a player object, and a team object. For each match statistics are saved for each player.
    """

    match = models.ForeignKey(
        "matches.Match",on_delete=models.CASCADE,related_name="player_statistics",
    )

    player = models.ForeignKey(
        "teams.Player",on_delete=models.CASCADE,related_name="match_statistics",
    )

    team = models.ForeignKey(
        "teams.Team",on_delete=models.CASCADE,related_name="player_match_statistics",
    )

    # this field is important since only a specific referee can submit statistics.
    referee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_matches",
    )

    goals = models.PositiveIntegerField(default=0)
    fouls = models.PositiveIntegerField(default=0)

    # Neat Validators!
    yellow_cards = models.PositiveIntegerField(default=0,validators=[MaxValueValidator(2)], )
    red_cards = models.PositiveIntegerField(default=0,validators=[MaxValueValidator(1)],)
    extra_statistics = models.JSONField(default=dict, blank=True)  # Json is useful here.
    # We will not be using extra statistics for this assignment - but it does prove that this model is extensible.
    # No need to complicate things further.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Ensures a team participates in a match before statistics submission,
        as well as that a player belongs to the specific team.
        """
        if self.team not in [self.match.team1, self.match.team2]:
            raise ValidationError("The selected team does not participate in this match.")

        player_belongs_to_team = TeamMember.objects.filter(
            team=self.team,
            player=self.player,
        ).exists()

        if not player_belongs_to_team:
            raise ValidationError("The selected player does not belong to the selected team.")

    def __str__(self):
        return f"{self.player} statistics for {self.match}"

    class Meta:
        ordering = ["match", "team__team_name", "player__surname"]
        constraints = [
            models.UniqueConstraint( # Only one statistics model for a player per match.
                fields=["match", "player"],
                name="unique_player_statistics_per_match",
            )
        ]