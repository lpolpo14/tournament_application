from django.db import models
from django.conf import settings




class UserDetails(models.Model):
    """
    Extends Django's User System by attaching a role to each user.
    Django's User model handles authentication while this model's role handles authorization.
    This allows us to keep Django's built in features while building on it.
    """

    class Role(models.TextChoices):
        SPORTS_ADMIN = 'sports_admin', "Sports Administrator"
        REFEREE = 'referee', "Referee"
        TEAM_MANAGER = 'team_manager', "Team Manager"

    # settings.AUTH_USER_MODEL is
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='details')

    role = models.CharField(max_length=20, choices=Role.choices)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
