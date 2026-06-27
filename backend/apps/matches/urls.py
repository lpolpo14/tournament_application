
from rest_framework.routers import DefaultRouter

from ..matches.views import MatchViewSet,StadiumViewSet

router = DefaultRouter()
router.register(r'matches', MatchViewSet, 'matches')
router.register(r"stadiums", StadiumViewSet, basename="stadium")

urlpatterns = router.urls