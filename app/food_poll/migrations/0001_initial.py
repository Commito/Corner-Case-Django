# Generated by Django 2.2 on 2019-04-04 00:56

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date(2019, 4, 4))),
                ('menu_items', models.TextField(max_length=5000)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='food_poll.Restaurant')),
            ],
        ),
    ]
