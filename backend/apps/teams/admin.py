from django.contrib import admin
from .models import Team, TeamMember, Player


# Register your models here.

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "surname", "main_shirt_number", "position"]
    search_fields = ["name", "surname"]
    list_filter = ["position"]

class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1 # Limits form number
    autocomplete_fields = ["player"] # Allows to add a player in line!

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    inlines = [TeamMemberInline]
    list_display = ["id", "team_name", "sport_name", "created_at"]
    search_fields = ["team_name", "sport_name"]
    list_filter = ["sport_name"]

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["id", "team", "player", "shirt_number", "joined_at"]
    search_fields = ["team__team_name", "player__name", "player__surname"]
    list_filter = ["team"]