from rest_framework import routers
from .api_views import ExpenseViewSet

router = routers.DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='api-expense')

urlpatterns = router.urls
