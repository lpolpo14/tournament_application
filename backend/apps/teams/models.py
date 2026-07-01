import uuid
from pathlib import Path

from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.db import models
from django.conf import settings
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
    ) # The player may have a preferred shirt number. A team can assign another number to a player.
    class Position(models.TextChoices):
        """
        Available player positions.

        In case the sport is not football, one can use unknown.
        """
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
        constraints = [ # Database level constraint - Ensures 1 <= Shirt Number <= 99
            CheckConstraint(condition=Q(main_shirt_number__gte=1) & Q(main_shirt_number__lte=99),
            name="player_main_shirt_number_between_1_and_99",
            )
        ]


# Improved version from https://www.youtube.com/watch?v=ZF-UZAxO18k
# uuid4 is unique compared to hash of file name.
def team_logo_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f"team_logos/{uuid.uuid4()}{extension}"

class Team(models.Model):
    """
    This model represents a team.
    """
    team_name = models.CharField(max_length=100)
    sport_name = models.CharField(max_length=100)

    manager = models.ForeignKey(settings.AUTH_USER_MODEL, # Best way to support custom user details.
                                on_delete=models.PROTECT, # Prevents deleting an user.
                                related_name='managed_teams', null=True, blank=True)

    # Optional team logo. Serializers perform further validation.
    logo_img = models.ImageField(upload_to=team_logo_upload_path,
                                 null=True,
                                 blank=True,
                                 validators=[FileExtensionValidator(
                                     allowed_extensions=["jpg", "jpeg", "png", "webp"])
                                 ]
                                 )


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
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='team_memberships')
    shirt_number = models.PositiveIntegerField() # The player's shirt number that he is wearing for team.
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.player.__str__()} of {self.team.team_name}'

    class Meta:
        ordering = ["team__team_name", "shirt_number"] # With __ we can gain access to team variables!
        constraints = [
            UniqueConstraint(fields=['team', 'player'], name="team_player_unique"),
            UniqueConstraint(fields=['team', 'shirt_number'], name="shirt_number_unique_per_team"),
            CheckConstraint(condition=Q(shirt_number__gte=1) & Q(shirt_number__lte=99),
                            name="team_main_shirt_number_between_1_and_99",
            )
        ]

