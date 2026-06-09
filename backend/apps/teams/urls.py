"""
An urls.py file. It is better to have multiple urls for cleaner pathing.
"""
from rest_framework.routers import DefaultRouter

from .views import TeamViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet, 'teams')

urlpatterns = router.urls