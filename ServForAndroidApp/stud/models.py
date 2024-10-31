from django.db import models

# Create your models here.


class Group(models.Model):
    group_name = models.CharField()


class Subjects(models.Model):
    group_id = models.ManyToManyField(Group)
    subject_name = models.CharField()


class UserSubject(models.Model):
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    teacher_id = models.ForeignKey('myapp.User', on_delete=models.CASCADE)


class Students(models.Model):
    name = models.CharField()
    surname = models.CharField()
    father_name = models.CharField()
    connect_address = models.CharField()
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)