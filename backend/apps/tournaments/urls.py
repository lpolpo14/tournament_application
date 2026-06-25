from rest_framework.routers import DefaultRouter

from .views import TournamentViewSet

router = DefaultRouter()

router.register("tournaments", TournamentViewSet, basename="tournaments")

urlpatterns = router.urls