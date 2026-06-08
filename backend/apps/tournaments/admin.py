from django.contrib import admin
from .models import Tournament,TournamentMatch


# Register your models here.
admin.site.register(TournamentMatch)
admin.site.register(Tournament)