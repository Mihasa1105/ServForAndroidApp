from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestViewSet, TestResultsViewSet

router = DefaultRouter()
router.register(r'tests', TestViewSet)
router.register(r'tests_results', TestResultsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
