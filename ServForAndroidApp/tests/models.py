from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Test(models.Model):
    user_id = models.ForeignKey('myapp.User', on_delete=models.CASCADE)
    question_quantity = models.IntegerField()
    subject_id = models.ForeignKey('stud.Subjects', on_delete=models.CASCADE)
    test_name = models.CharField(max_length=255)
    answers = models.JSONField()
    tags = ArrayField(models.CharField(max_length=50), blank=True)


class TestResults(models.Model):
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    student_id = models.ForeignKey('stud.Students', on_delete=models.CASCADE)
    answers = models.JSONField()

