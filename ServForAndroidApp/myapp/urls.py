from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserCodeViewSet

router = DefaultRouter()
router.register(r'teachers', UserViewSet)
router.register(r'user_code', UserCodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
