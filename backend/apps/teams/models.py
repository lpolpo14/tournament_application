from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint


# Create your models here.

class Player(models.Model):
    """
    This model represents a player in the team.
    """
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    main_shirt_number =  models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
    )
    class Position(models.TextChoices):
        GOALKEEPER = "GK", "Goalkeeper"
        DEFENDER = "DF", "Defender"
        MIDFIELDER = "MF", "Midfielder"
        FORWARDER = "FR", "Forward"
        UNKNOWN = "UK", "Unknown"
    position = models.CharField(choices=Position.choices, max_length=2, default=Position.UNKNOWN)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} {self.surname}'

    class Meta:
        ordering = ['surname', 'name']
        constraints = [
            CheckConstraint(condition=Q(main_shirt_number__gte=1) & Q(main_shirt_number__lte=99),
            name="player_main_shirt_number_between_1_and_99",
            )
        ]


class Team(models.Model):
    """
    This model represents a team.
    """
    team_name = models.CharField(max_length=100)
    sport_name = models.CharField(max_length=100)
    # logo_img = models.ImageField(upload_to='team_logo', null=True, blank=True)
    # We will add image later.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['team_name']
        constraints = [
            UniqueConstraint(fields=['team_name', 'sport_name'], name="team_name_sport_name_unique"),
        ]

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
    shirt_number = models.PositiveIntegerField() # In case a player is in multiple teams. Might remove later
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.player.__str__()} of {self.team.team_name}'

    class Meta:
        ordering = ["team__team_name", "shirt_number"] # With __ we can gain access to team variables!
        constraints = [
            UniqueConstraint(fields=['team', 'player'], name="team_player_unique"),
            UniqueConstraint(fields=['team', 'shirt_number'], name="shirt_number_unique_per_team"),
            CheckConstraint(condition=Q(shirt_number=1) & Q(shirt_number=99),
                            name="team_main_shirt_number_between_1_and_99",
            )
        ]

