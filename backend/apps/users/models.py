from django.db import models
from django.conf import settings




class UserDetails(models.Model):

    class Role(models.TextChoices):
        SPORTS_ADMIN = 'sports_admin', "Sports Administrator"
        REFEREE = 'referee', "Referee"
        TEAM_MANAGER = 'team_manager', "Team Manager"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='details')

    role = models.CharField(max_length=20, choices=Role.choices)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
