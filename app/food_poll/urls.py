from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('restaurants', views.RestaurantView)
router.register('menus', views.MenuView)
router.register('menuvotes', views.MenuVoteView, base_name='menuvote')
router.register('users', views.UserViewSet)
router.register('profile', views.ProfileViewSet)
router.register('log_entries', views.LogEntryView)

urlpatterns = [
    path('', include(router.urls))
]
