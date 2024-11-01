from django.contrib import admin
from .models import Group, Students, Subjects, UserSubject


admin.site.register(Group)
admin.site.register(Subjects)
admin.site.register(UserSubject)
admin.site.register(Students)
