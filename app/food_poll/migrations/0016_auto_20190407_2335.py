# Generated by Django 2.2 on 2019-04-07 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('food_poll', '0015_auto_20190407_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='food_poll.Restaurant'),
        ),
    ]
