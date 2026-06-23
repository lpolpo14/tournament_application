"""
An urls.py file. It is better to have multiple urls for cleaner pathing.
"""
from rest_framework.routers import DefaultRouter

from .views import TeamViewSet, PlayerViewSet, TeamMemberViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet, 'teams')
router.register(r'players', PlayerViewSet, 'players')
router.register(r'team-members', TeamMemberViewSet, 'team-members')

urlpatterns = router.urls