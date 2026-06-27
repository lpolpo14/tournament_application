from django.core.exceptions import ValidationError
from django.db import models



class Match(models.Model):
    """
    This model represents a match between two teams.
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
    team1_score = models.PositiveIntegerField(null=True, blank=True) # No need for immediate initialization.
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    match_status = models.CharField(max_length=100,choices=Status.choices, default='Scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.team1} vs {self.team2}'

    def clean(self):
        if self.team1 == self.team2:
            raise ValidationError('Teams must be different.')

class Stadium(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.name} - {self.city}"
