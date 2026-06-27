
from rest_framework.routers import DefaultRouter

from ..matches.views import MatchViewSet,StadiumViewSet, PlayerMatchStatisticsViewSet

router = DefaultRouter()
router.register(r'matches', MatchViewSet, 'matches')
router.register(r"stadiums", StadiumViewSet, basename="stadium")
router.register(r"player-match-statistics",PlayerMatchStatisticsViewSet,basename="player-match-statistics",)

urlpatterns = router.urls