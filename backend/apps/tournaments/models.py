from datetime import timezone

from django.db import models
from django.db.models import Q, F
from rest_framework.exceptions import ValidationError



class Tournament(models.Model):
    name = models.CharField(max_length=100)
    sport = models.CharField(max_length=100)
    teams = models.ManyToManyField('teams.Team',blank=True, related_name='tournamentParticipation')
    location = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    class Status(models.TextChoices):
        SCHEDULED = "Scheduled", "Scheduled"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"
        ONGOING = "Ongoing", "Ongoing"
    status = models.CharField(max_length=100, choices= Status.choices, default='Scheduled')

    def __str__(self):
        return f'{self.name} ({self.start_date} to {self.end_date})'

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('Start date must be before end date')

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gt=F("start_date")), # F makes it possible to refer to model field values and perform database operations using them without actually having to pull them out of the database into Python memory.
                name="tournament_end_after_start",
            )
        ]

class TournamentParticipation(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        ACCEPTED = "Accepted", "Accepted"
        REJECTED = "Rejected", "Rejected"

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participations')

    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='tournament_participations')

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    requested_at = models.DateTimeField(auto_now_add=True)
    request_answered_at = models.DateTimeField(null=True, blank=True)

    def accept(self):
        self.status = self.Status.ACCEPTED
        self.request_answered_at= timezone.now()
        self.save()
        self.tournaments.teams.add(self.team)

    def reject(self):
        self.status = self.Status.REJECTED
        self.request_answered_at = timezone.now()
        self.save()
        self.tournaments.teams.remove(self.team) # Just in case

    def __str__(self):
        return f'Team {self.team} participation status for tournament {self.tournament.name}: {self.status}'
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tournament', 'team'],
                name="tournament_participation_unique"
            )
        ]

"""
This might not be needed.
class TournamentMatch(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE) # String imports are best practice.
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.match.__str__()} of {self.tournament.name}'
"""
