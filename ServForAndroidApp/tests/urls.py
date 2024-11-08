from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestViewSet, TestResultsViewSet, TestImageViewSet

router = DefaultRouter()
router.register(r'tests', TestViewSet)
router.register(r'tests_results', TestResultsViewSet)
router.register(r'tests_image', TestImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
