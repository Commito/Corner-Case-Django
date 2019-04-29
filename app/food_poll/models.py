import datetime

from django.contrib.auth.models import User
from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Menu(models.Model):
    class Meta:
        unique_together = (('restaurant', 'date'),)

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    description = models.TextField(max_length=5000)

    @property
    def menuvotes(self):
        return self.menuvote_set.values() or []

    @property
    def totalvotes(self):
        return len(self.menuvote_set.values()) or 0

    def __str__(self):
        return self.restaurant.name + " " + str(self.date)


class MenuVote(models.Model):
    class Meta:
        unique_together = (('menu', 'user'),)

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='menuvotes',
                             on_delete=models.CASCADE)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee = models.BooleanField(default=False)
    restaurants = models.ManyToManyField(Restaurant, blank=True, null=True)

    def __str__(self):
        return self.user.username
