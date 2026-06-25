from django.db import models


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    sport = models.CharField(max_length=100)
    teams = models.ManyToManyField('teams.Team', related_name='tournamentParticipation')
    location = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=100, default='Scheduled')

    def __str__(self):
        return f'{self.name} ({self.start_date} to {self.end_date})'

"""
This might not be needed.
class TournamentMatch(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE) # String imports are best practice.
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.match.__str__()} of {self.tournament.name}'
"""
