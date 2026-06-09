from django.db import models




class Match(models.Model):
    """
    This model represents a match between two teams.
    """
    team1 = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='team1_matches')
    team2 = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='team2_matches')
    date = models.DateField()
    location = models.CharField(max_length=255) # Where the match takes place.
    team1_score = models.PositiveIntegerField(null=True, blank=True) # No need for immediate initialization.
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    match_status = models.CharField(max_length=100, default='Scheduled')

    def __str__(self):
        return f'{self.team1} vs {self.team2}'
