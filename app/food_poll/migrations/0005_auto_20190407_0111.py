# Generated by Django 2.2 on 2019-04-06 22:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food_poll', '0004_auto_20190404_0437'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='menu',
            unique_together={('restaurant', 'date')},
        ),
    ]