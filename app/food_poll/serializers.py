from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_tracking.models import APIRequestLog

from .models import Restaurant, Menu, MenuVote, Profile


class RestaurantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'url')

    def create(self, validated_data):
        restaurant = Restaurant.objects.create(name=validated_data.get('name'))
        profile = Profile.objects.filter(
            user=self.context['request'].user).first()
        if not profile:
            profile = Profile.objects.create(user=self.context['request'].user)
        profile.restaurants.add(restaurant)
        return restaurant


class MenuVoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MenuVote
        fields = ('id', 'url', 'menu', 'user')


class MenuSerializer(serializers.HyperlinkedModelSerializer):
    menuvotes = serializers.SerializerMethodField()
    voted = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ('id', 'url', 'date', 'restaurant', 'description',
                  'menuvotes', 'totalvotes', 'voted')

    def get_menuvotes(self, obj):
        return [MenuVoteSerializer(
            menuvote, context={'request': self.context['request']}
        ).data for menuvote in obj.menuvote_set.all()]

    def get_voted(self, obj):
        return bool(obj.menuvote_set.filter(
            user=self.context['request'].user
        ).first())

    def create(self, validated_data):
        profile = Profile.objects.filter(
            user=self.context['request'].user
        ).first()
        if profile or self.context['request'].user.is_superuser:
            if self.context['request'].user.is_superuser or \
                    validated_data.get('restaurant') in \
                    profile.restaurants.all():
                menu = super(MenuSerializer, self).create(validated_data)
                menu.save()
                return menu
            else:
                raise serializers.ValidationError(
                    "User is not an employee of restaurant " +
                    validated_data.get('restaurant').name)
        else:
            raise serializers.ValidationError("No profile found")

    def get_field_names(self, *args, **kwargs):
        field_names = self.context.get('fields', None)
        if field_names:
            return field_names

        return super(MenuSerializer, self).get_field_names(*args, **kwargs)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(
        view_name='profile-detail', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'password', 'profile')

    def create(self, validated_data):
        user = User.objects.filter(
            username=validated_data.get('username')).first()
        if user:
            raise serializers.ValidationError(
                "User with username " + user.username + " already exists")
        user = User(username=validated_data.get('username'),
                    email=validated_data.get('email', 'example@example.com'))
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    def update(self, instance, validated_data):
        if validated_data.get('username') or validated_data.get('password'):
            if validated_data.get('username'):
                instance.username = validated_data.get('username')
            if validated_data.get('password'):
                instance.set_password(validated_data.get('password'))
            instance.save()

        return instance


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'url', 'user', 'employee', 'restaurants')

    def create(self, validated_data):
        profile = Profile.objects.create(
            user=validated_data.get('user'),
            employee=validated_data.get('employee', False))
        profile.restaurants.set(validated_data.get('restaurants', []))
        return profile


class LogEntrySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = APIRequestLog
        fields = (
            'id', 'url', 'requested_at', 'response_ms', 'path',
            'remote_addr', 'host', 'method', 'query_params', 'data',
            'response', 'status_code', 'view', 'view_method', 'errors',
            'user_id'
        )
