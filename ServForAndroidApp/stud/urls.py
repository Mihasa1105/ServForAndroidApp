from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, StudViewSet, GroupViewSet, UserSubjectViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'students', StudViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'usersubjects', UserSubjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
