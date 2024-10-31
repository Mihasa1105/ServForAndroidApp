from django.urls import path
from .views import CreateTestView

urlpatterns = [
    path('create-test/', CreateTestView.as_view(), name='create-test'),
]
