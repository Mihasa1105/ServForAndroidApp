# Generated by Django 5.1.2 on 2025-02-09 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0002_testimage_testresults_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresults',
            name='mark',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testresults',
            name='points',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
