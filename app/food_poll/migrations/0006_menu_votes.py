# Generated by Django 2.2 on 2019-04-06 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_poll', '0005_auto_20190407_0111'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='votes',
            field=models.IntegerField(default=0),
        ),
    ]
