"""
An urls.py file. It is better to have multiple urls for cleaner pathing.
"""
from rest_framework.routers import DefaultRouter

from .views import TeamViewSet, PlayerViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet, 'teams')
router.register(r'players', PlayerViewSet, 'players')

urlpatterns = router.urls