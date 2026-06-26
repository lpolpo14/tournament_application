from rest_framework.routers import DefaultRouter

from .views import TournamentViewSet, TournamentParticipationViewSet

router = DefaultRouter()

router.register("tournaments", TournamentViewSet, basename="tournaments")
router.register(r"tournament-registrations", TournamentParticipationViewSet,
                basename="tournament-registration",)

urlpatterns = router.urls