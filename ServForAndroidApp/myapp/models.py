from django.db import models

# Create your models here.


class User(models.Model):
    name = models.CharField()
    surname = models.CharField()
    father_name = models.CharField()
    is_admin = models.BooleanField()


class UserCode(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.IntegerField()

