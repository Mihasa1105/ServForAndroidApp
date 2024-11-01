from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestViewSet

router = DefaultRouter()
router.register(r'tests', TestViewSet)  # Это создаст маршруты для CRUD операций

urlpatterns = [
    path('', include(router.urls)),  # Включаем все маршруты, зарегистрированные в router
]
