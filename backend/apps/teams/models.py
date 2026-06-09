from django.db import models

# Create your models here.

class Player(models.Model):
    """
    This model represents a player in the team.
    """
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    main_shirt_number =  models.PositiveIntegerField()

    def __str__(self):
        return f'{self.name} {self.surname}'


class Team(models.Model):
    """
    This model represents a team.
    """
    team_name = models.CharField(max_length=100)
    sport_name = models.CharField(max_length=100)
    # logo_img = models.ImageField(upload_to='team_logo', null=True, blank=True)
    # We will add image later.

    class Meta:
        ordering = ['team_name']

    def __str__(self):
        return f'{self.team_name}'

class TeamMember(models.Model):
    """
    This model represents the relations between a specific team and its players.
    Specifically, every object is a 1-1 relationship between a player and his respective team.
    This is flexible design.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    shirt_number = models.PositiveIntegerField() # In case a player is in multiple teams.
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.__str__()} of {self.team.team_name}'

