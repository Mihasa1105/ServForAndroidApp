from django.contrib import admin
from .models import User, UserCode  # импортируйте модели

admin.site.register(User)
admin.site.register(UserCode)
