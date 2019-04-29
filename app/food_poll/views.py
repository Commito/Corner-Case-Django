import datetime

from django.contrib.auth.models import User
from django.http import QueryDict
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import list_route, action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_tracking.models import APIRequestLog

from .mixins import ConfiguredLoggingMixin
from .helpers import get_updated_serializer_fields, get_permissions_by_action
from .permissions import IsRestaurantEmployee, IsEmployee, IsUser
from .models import Restaurant, Menu, Profile, MenuVote
from .serializers import RestaurantSerializer, MenuSerializer, \
    MenuVoteSerializer, ProfileSerializer, UserSerializer, LogEntrySerializer

menuview_fields = ['id', 'url', 'restaurant', 'date', 'description', 'voted']


class RestaurantView(ConfiguredLoggingMixin, viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsRestaurantEmployee | permissions.DjangoObjectPermissions,)

    @action(detail=True)
    def today(self, request, *args, **kwargs):
        queryset = Menu.objects.filter(restaurant=kwargs.get('pk'),
                                       date=datetime.date.today()).first()
        data = MenuSerializer(queryset, context={
            'request': self.request, 'fields': menuview_fields},)
        return Response(data.data)


class MenuView(ConfiguredLoggingMixin, viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsRestaurantEmployee | permissions.DjangoObjectPermissions,)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.queryset.filter(id=kwargs.get('pk')).first()
        serializer = MenuSerializer(queryset, context={
            'request': request,
            'fields': menuview_fields
        })
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        serializer = MenuSerializer(queryset, context={
            'request': request,
            'fields': menuview_fields
        }, many=True)

        return Response(serializer.data)

    @list_route()
    def results(self, request, *args, **kwargs):
        queryset = self.queryset.filter(date=datetime.date.today())

        fields = get_updated_serializer_fields(
            menuview_fields + ['totalvotes'],
            request.user.is_superuser, ['menuvotes']
        )
        serializer = MenuSerializer(queryset, context={
            'request': request,
            'fields': fields
        }, many=True)

        return Response(serializer.data)

    @list_route()
    def today(self, request, *args, **kwargs):
        queryset = self.queryset.filter(date=datetime.date.today())
        serializer = MenuSerializer(queryset, context={
            'request': request,
            'fields': menuview_fields
        }, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[
        permissions.IsAuthenticatedOrReadOnly, IsEmployee])
    def vote(self, request, pk):
        menuvote = MenuVote.objects.filter(menu=pk, user=request.user).first()
        menu = Menu.objects.filter(pk=pk).first()
        if menuvote:
            menuvote.delete()
            return Response({
                'voted': False,
                'message': "Vote for " + str(menu) + " removed"
            })
        elif menu:
            MenuVote.objects.create(user=request.user, menu=menu)
            return Response({
                'voted': True,
                'message': "You have voted for " + str(menu) + " lunch menu"
            })
        raise ValidationError("Menu was not found")


class MenuVoteView(viewsets.ModelViewSet):
    queryset = MenuVote.objects.all()
    serializer_class = MenuVoteSerializer
    permission_classes = (permissions.IsAdminUser,)
    http_method_names = ['get', 'options', 'head']


class UserViewSet(ConfiguredLoggingMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes_by_action = {
        'create': [],
        'list': [permissions.IsAuthenticated],
        'retrieve': [IsUser],
        'partial_update': [
            IsUser | permissions.DjangoObjectPermissions
        ],
        'update': [
            IsUser | permissions.DjangoObjectPermissions
        ],
        'destroy': [IsUser | permissions.DjangoObjectPermissions]
     }

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        if not self.request.user.is_superuser:
            queryset = queryset.filter(id=self.request.user.id)
        serializer = UserSerializer(queryset, context={'request': request},
                                    many=True)

        return Response(serializer.data)

    def get_permissions(self):
        return get_permissions_by_action(self.permission_classes_by_action,
                                         self.action, self.permission_classes)

    def create(self, request, *args, **kwargs):
        serialized = UserSerializer().create(self.request.data)
        serialized_dict = self.request.data.copy()
        serialized_dict['user'] = serialized

        if not self.request.user.is_superuser:
            serialized_dict['employee'] = False
            serialized_dict['restaurants'] = []

        qdict = QueryDict('', mutable=True)
        qdict.update(serialized_dict)

        ProfileSerializer(data=qdict).create(qdict)

        serialized = UserSerializer(serialized, context={'request': request})
        return Response(serialized.data, status=status.HTTP_201_CREATED)


class ProfileViewSet(ConfiguredLoggingMixin, viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoObjectPermissions
    )
    http_method_names = ['get', 'options', 'head', 'put', 'patch']


class LogEntryView(viewsets.ModelViewSet):
    queryset = APIRequestLog.objects.all()
    serializer_class = LogEntrySerializer
    permission_classes = (permissions.IsAdminUser,)
    http_method_names = ['get', 'options', 'head']
