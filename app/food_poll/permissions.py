from rest_framework import permissions

from .models import Profile


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsEmployee(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        profile = Profile.objects.filter(user=request.user).first()
        return profile and profile.employee

    def has_object_permission(self, request, view, obj):
        profile = Profile.objects.filter(user=request.user).first()

        if request.method in permissions.SAFE_METHODS:
            return True

        return profile and profile.employee


class IsRestaurantEmployee(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated or request.user.is_anonymous:
            return False

        profiles = Profile.objects.filter(user=request.user).first()

        if not profiles:
            return False

        restaurants = profiles.restaurants.all()

        if not restaurants:
            return False

        if view.basename == 'restaurant':
            if obj in restaurants:
                return True
        elif view.basename == 'menu':
            if obj.restaurant in restaurants:
                return True

        return False


class IsUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_superuser:
            return True
        return obj == request.user
