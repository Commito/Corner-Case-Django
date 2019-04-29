# Generated by Django 2.2 on 2019-04-07 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_poll', '0009_auto_20190407_0243'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='num_vote_down',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='menu',
            name='num_vote_up',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='menu',
            name='vote_score',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
