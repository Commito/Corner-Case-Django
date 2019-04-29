import base64
import datetime
import uuid

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework.utils.serializer_helpers import ReturnList

from .models import Restaurant, Menu, MenuVote, Profile
from rest_framework_tracking.models import APIRequestLog

User = get_user_model()
client = APIClient()

RESTAURANTS_URL = '/restaurants/'
MENUS_URL = '/menus/'
MENUVOTES_URL = '/menuvotes/'
LOG_ENTRIES_URL = '/log_entries/'
USERS_URL = '/users/'
PROFILES_URL = '/profile/'

USER_USERNAME = 'test_user'
USER_PASSWORD = 'test_user'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '94a610c6-db55-4fab-acaa-d34e1c21412d'
ADMIN_EMAIL = 'admin@test.com'


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD
        )
        self.admin.save()

        self.anonymous_client = APIClient()
        response = self.anonymous_client.post(USERS_URL, {
            'username': USER_USERNAME,
            'password': USER_PASSWORD
        })
        self.user = response.data

        self.admin_client = APIClient()
        self.admin_client.login(username=ADMIN_USERNAME,
                                password=ADMIN_PASSWORD)
        self.user_client = APIClient()
        self.user_client.login(username=USER_USERNAME, password=USER_PASSWORD)
        self.employee = self.admin_client.post(USERS_URL, {
            'username': 'employee',
            'password': 'employee',
            'employee': True
        })


class RestaurantAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        response = self.user_client.post(RESTAURANTS_URL,
                                         {"name": 'test_restaurant'})
        self.restaurant_id = response.data.get('id')

        restaurant_2 = Restaurant.objects.create(name='test_restaurant_2')
        self.restaurant_2_id = restaurant_2.id

        self.RESTAURANT_CREATED_BY_USER_URL = \
            RESTAURANTS_URL + str(self.restaurant_id) + '/'
        self.RESTAURANT_CREATED_BY_ADMIN_URL = \
            RESTAURANTS_URL + str(self.restaurant_2_id) + '/'

    def test_create_restaurant(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_201_CREATED,
            'admin': status.HTTP_201_CREATED
        }

        data = {'name': 'test_restaurant'}

        responses = create_responses(self, RESTAURANTS_URL, data)
        check_responses(self, responses, status_codes)

    def test_get_restaurants(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_200_OK,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, RESTAURANTS_URL)
        check_responses(self, responses, status_codes)

        self.assertGreater(len(responses['user'].data), 0)

    def test_get_restaurant(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_200_OK,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, self.RESTAURANT_CREATED_BY_USER_URL)
        check_responses(self, responses, status_codes)

        self.assertTrue(responses['user'].data)

    def test_update_restaurant(self):
        response = client.get(self.RESTAURANT_CREATED_BY_USER_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        resp_user = self.user_client.put(self.RESTAURANT_CREATED_BY_USER_URL,
                                         {'name': 'test_restaurant edited'})
        self.assertEqual(resp_user.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_user.data.get('name'), 'test_restaurant edited')

        resp_user = self.user_client.put(self.RESTAURANT_CREATED_BY_ADMIN_URL,
                                         {'name': 'test_restaurant_2 edited'})
        self.assertEqual(resp_user.status_code, status.HTTP_403_FORBIDDEN)

        resp_admin = self.admin_client.put(
            self.RESTAURANT_CREATED_BY_USER_URL,
            {'name': 'test_restaurant edited by admin'}
        )
        self.assertEqual(resp_admin.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_admin.data.get('name'),
                         'test_restaurant edited by admin')

    def test_delete_restaurant(self):
        status_codes_for_user = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_204_NO_CONTENT,
            'admin': status.HTTP_404_NOT_FOUND
        }

        user_reponses = delete_responses(self,
                                         self.RESTAURANT_CREATED_BY_USER_URL)
        check_responses(self, user_reponses, status_codes_for_user)

        restaurant = Restaurant.objects.filter(id=self.restaurant_id).first()
        self.assertEqual(restaurant, None)

        status_codes_for_admin = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_204_NO_CONTENT
        }

        admin_responses = delete_responses(
            self, self.RESTAURANT_CREATED_BY_ADMIN_URL)
        check_responses(self, admin_responses, status_codes_for_admin)

    def test_get_todays_menu(self):
        TODAYS_MENU_URL = RESTAURANTS_URL + str(self.restaurant_id) + '/today/'

        response = client.get(TODAYS_MENU_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        resp_user = self.user_client.get(TODAYS_MENU_URL)
        self.assertEqual(resp_user.status_code, status.HTTP_200_OK)
        self.assertTrue(resp_user.data)


class MenuAPITestCase(RestaurantAPITestCase):

    def setUp(self):
        super().setUp()
        self.restaurant = Restaurant.objects.filter(
            id=self.restaurant_id
        ).first()
        self.menu = Menu.objects.create(
            restaurant=self.restaurant,
            date=datetime.date.today(),
            description="Menu description"
        )
        self.restaurant_2 = Restaurant.objects.filter(
            id=self.restaurant_2_id
        ).first()
        self.menu_2 = Menu.objects.create(
            restaurant=self.restaurant_2,
            date=datetime.date.today(),
            description="Menu 2 description"
        )

        self.MENU_FOR_RESTAURANT_CREATED_BY_USER_URL = \
            MENUS_URL + str(self.menu.id) + '/'
        self.MENU_FOR_RESTAURANT_CREATED_BY_ADMIN_URL = \
            MENUS_URL + str(self.menu_2.id) + '/'

    def test_create_menu(self):
        data_for_user = {
            'restaurant': '/restaurants/' + str(self.restaurant_id) + '/',
            'date': datetime.date.today() + datetime.timedelta(days=1),
            'description': "Menu description"
        }

        status_codes_for_user = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_201_CREATED,
            'admin': status.HTTP_400_BAD_REQUEST
        }

        user_responses = create_responses(self, MENUS_URL, data_for_user)
        check_responses(self, user_responses, status_codes_for_user)

        data_for_admin = {
            'restaurant': '/restaurants/' + str(self.restaurant_2_id) + '/',
            'date': datetime.date.today() + datetime.timedelta(days=1),
            'description': "Menu 2 description"
        }

        status_codes_for_admin = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_400_BAD_REQUEST,
            'admin': status.HTTP_201_CREATED
        }

        admin_responses = create_responses(self, MENUS_URL, data_for_admin)
        check_responses(self, admin_responses, status_codes_for_admin)

    def test_get_menus(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_200_OK,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, MENUS_URL)

        check_responses(self, responses, status_codes)

        self.assertGreater(len(responses['user'].data), 0)

    def test_get_menu(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_200_OK,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, self.RESTAURANT_CREATED_BY_USER_URL)

        check_responses(self, responses, status_codes)

        self.assertTrue(responses['user'].data)

    def test_update_menu(self):
        response = client.patch(
            self.MENU_FOR_RESTAURANT_CREATED_BY_USER_URL,
            {'description': 'Menu description edited by anonymous user'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        resp_user = self.user_client.patch(
            self.MENU_FOR_RESTAURANT_CREATED_BY_USER_URL,
            {'description': 'Menu description edited by user'}
        )
        self.assertEqual(resp_user.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_user.data.get('description'),
                         'Menu description edited by user')

        resp_user = self.user_client.patch(
            self.MENU_FOR_RESTAURANT_CREATED_BY_ADMIN_URL,
            {'description': 'Menu description 2 edited by user'}
        )
        self.assertEqual(resp_user.status_code, status.HTTP_403_FORBIDDEN)

        resp_admin = self.admin_client.patch(
            self.MENU_FOR_RESTAURANT_CREATED_BY_ADMIN_URL,
            {'description': 'Menu description 2 edited by admin'}
        )
        self.assertEqual(resp_admin.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_admin.data.get('description'),
                         'Menu description 2 edited by admin')

    def test_delete_menu(self):
        status_codes_for_user = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_204_NO_CONTENT,
            'admin': status.HTTP_404_NOT_FOUND
        }

        status_codes_for_admin = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_204_NO_CONTENT
        }

        user_responses = delete_responses(
            self, self.RESTAURANT_CREATED_BY_USER_URL)
        check_responses(self, user_responses, status_codes_for_user)

        menu = Menu.objects.filter(id=self.menu.id).first()
        self.assertEqual(menu, None)

        admin_responses = delete_responses(
            self, self.RESTAURANT_CREATED_BY_ADMIN_URL)
        check_responses(self, admin_responses, status_codes_for_admin)

    def test_menu_voting(self):
        MENU_VOTE_URL = MENUS_URL + str(self.menu.id) + '/vote/'

        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_403_FORBIDDEN
        }

        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(
                b'employee:employee').decode("ascii")
        }

        responses = create_responses(self, MENU_VOTE_URL, {})
        check_responses(self, responses, status_codes)

        resp_employee = client.post(MENU_VOTE_URL, **auth_headers)
        self.assertEqual(resp_employee.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_employee.data.get('voted'), True)

        resp_employee = client.post(MENU_VOTE_URL, **auth_headers)
        self.assertEqual(resp_employee.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_employee.data.get('voted'), False)

    def test_get_todays_menus(self):
        TODAYS_MENUS_URL = MENUS_URL + 'today/'

        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_200_OK,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, TODAYS_MENUS_URL)
        check_responses(self, responses, status_codes)

        self.assertGreater(len(responses['user'].data), 0)

    def test_get_menu_results_for_today(self):
        TODAYS_MENUS_RESULTS_URL = MENUS_URL + 'results/'

        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_200_OK,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, TODAYS_MENUS_RESULTS_URL)
        check_responses(self, responses, status_codes)

        self.assertGreater(len(responses['user'].data), 0)
        self.assertGreater(len(responses['admin'].data), 0)


class MenuVoteAPITestCase(MenuAPITestCase):

    def setUp(self):
        super().setUp()

        user = User.objects.filter(id=self.user.get('id')).first()
        self.menuvote = MenuVote.objects.create(user=user, menu=self.menu)
        self.MENUVOTE_URL = MENUVOTES_URL + str(self.menuvote.id) + '/'

    def test_menuvote_create(self):
        data = {
            'user': '/users/' + str(self.user.get('id')) + '/',
            'menu': '/menus/' + str(self.menu.id) + '/'
        }

        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_405_METHOD_NOT_ALLOWED
        }

        responses = update_responses(self, MENUVOTES_URL, data)
        check_responses(self, responses, status_codes)

    def test_menuvote_update(self):
        data = {
            'user': '/users/' + str(self.admin.id) + '/',
            'menu': '/menus/' + str(self.menu_2.id) + '/'
        }

        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_405_METHOD_NOT_ALLOWED
        }

        responses = update_responses(self, self.MENUVOTE_URL, data)
        check_responses(self, responses, status_codes)

    def test_menuvote_delete(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_405_METHOD_NOT_ALLOWED
        }

        responses = delete_responses(self, self.MENUVOTE_URL)
        check_responses(self, responses, status_codes)

    def test_get_menuvotes(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, MENUVOTES_URL)
        check_responses(self, responses, status_codes)

        self.assertGreater(len(responses['admin'].data), 0)

    def test_get_menuvote(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, self.MENUVOTE_URL)
        check_responses(self, responses, status_codes)

        self.assertTrue(responses['admin'].data)


class LogEntryAPITestCase(MenuVoteAPITestCase):

    def setUp(self):
        super().setUp()

        self.log_entry = APIRequestLog.objects.first()
        self.LOG_ENTRY_URL = LOG_ENTRIES_URL + str(self.log_entry.id) + '/'

    def test_get_log_entries(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, LOG_ENTRIES_URL)
        check_responses(self, responses, status_codes)

        self.assertGreater(len(responses['admin'].data), 0)

    def test_get_log_entry(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, self.LOG_ENTRY_URL)
        check_responses(self, responses, status_codes)

        self.assertTrue(responses['admin'].data)

    def test_log_entry_create(self):
        data = {
            "requested_at": "2019-04-18T03:08:39.415731Z",
            "response_ms": 309,
            "path": "/profile/",
            "remote_addr": "127.0.0.1",
            "host": "localhost:8000",
            "method": "GET",
            "query_params": "{}",
            "data": "{}",
            "response": "",
            "status_code": 200,
            "view": "food_poll.views.ProfileViewSet",
            "view_method": "list",
            "errors": "",
            "user_id": 1
        }

        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_405_METHOD_NOT_ALLOWED
        }

        responses = create_responses(self, LOG_ENTRIES_URL, data)
        check_responses(self, responses, status_codes)

    def test_log_entry_update(self):
        data = {
            "method": "OPTIONS",
            "status_code": 100,
            "path": "/Path/",
        }

        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_405_METHOD_NOT_ALLOWED
        }

        responses = update_responses(self, self.LOG_ENTRY_URL, data)
        check_responses(self, responses, status_codes)

    def test_log_entry_delete(self):

        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_405_METHOD_NOT_ALLOWED
        }

        responses = delete_responses(self, self.LOG_ENTRY_URL)
        check_responses(self, responses, status_codes)


class UserAPITestCase(RestaurantAPITestCase):

    def setUp(self):
        super().setUp()

        self.user_object = User.objects.filter(id=self.user.get('id')).first()
        self.USER_URL = USERS_URL + str(self.user.get('id')) + '/'
        self.ADMIN_USER_URL = USERS_URL + str(self.admin.id) + '/'

    def test_get_users(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_200_OK,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, USERS_URL)
        check_responses(self, responses, status_codes)

        self.assertNotEqual(type(responses['anonymous'].data), ReturnList)
        self.assertEqual(type(responses['user'].data), ReturnList)
        self.assertEqual(len(responses['user'].data), 1)
        self.assertEqual(type(responses['admin'].data), ReturnList)
        self.assertGreater(len(responses['admin'].data), 1)

    def test_get_user(self):
        data = {
            'user': {
                'url': self.USER_URL,
                'status_codes': {
                    'anonymous': status.HTTP_403_FORBIDDEN,
                    'user': status.HTTP_200_OK,
                    'admin': status.HTTP_200_OK
                }
            },
            'admin': {
                'url': self.ADMIN_USER_URL,
                'status_codes': {
                    'anonymous': status.HTTP_403_FORBIDDEN,
                    'user': status.HTTP_403_FORBIDDEN,
                    'admin': status.HTTP_200_OK
                }
            }
        }

        for key, value in data.items():
            responses = get_responses(self, value.get('url'))
            check_responses(self, responses, value.get('status_codes'))

    def test_user_create(self):
        data = {
            "username": "Useris",
            "password": "Useris"
        }

        response = client.post(USERS_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_update(self):
        request_data = {
            'user': {
                'url': self.USER_URL,
                'status_codes': {
                    'anonymous': status.HTTP_403_FORBIDDEN,
                    'user': status.HTTP_200_OK,
                    'admin': status.HTTP_200_OK
                }
            },
            'admin': {
                'url': self.ADMIN_USER_URL,
                'status_codes': {
                    'anonymous': status.HTTP_403_FORBIDDEN,
                    'user': status.HTTP_403_FORBIDDEN,
                    'admin': status.HTTP_200_OK
                }
            }
        }

        for key, value in request_data.items():
            responses = update_responses(
                self, value.get('url'), {}, "username")
            check_responses(self, responses, value.get('status_codes'))

    def test_log_entry_delete(self):
        data = {
            'user': {
                'url': self.USER_URL,
                'status_codes': {
                    'anonymous': status.HTTP_403_FORBIDDEN,
                    'user': status.HTTP_204_NO_CONTENT,
                    'admin': status.HTTP_404_NOT_FOUND
                },
                'id': self.user.get('id')
            },
            'admin': {
                'url': self.ADMIN_USER_URL,
                'status_codes': {
                    'anonymous': status.HTTP_403_FORBIDDEN,
                    'user': status.HTTP_403_FORBIDDEN,
                    'admin': status.HTTP_204_NO_CONTENT
                },
                'id': self.admin.id
            }
        }

        for key, value in data.items():
            responses = delete_responses(self, value.get('url'))
            check_responses(self, responses, value.get('status_codes'))

            APIRequestLog.objects.filter(user_id=value.get('id')).delete()


class ProfileAPITestCase(RestaurantAPITestCase):

    def setUp(self):
        super().setUp()

        self.profile_object = Profile.objects.filter(
            user=self.user.get('id')
        ).first()
        self.PROFILE_URL = PROFILES_URL + str(self.profile_object.id) + '/'

    def test_get_profiles(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_200_OK,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, PROFILES_URL)
        check_responses(self, responses, status_codes)

    def test_get_profile(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_200_OK,
            'admin': status.HTTP_200_OK
        }

        responses = get_responses(self, self.PROFILE_URL)
        check_responses(self, responses, status_codes)

    def test_profile_create(self):
        data = {
            "user": str(self.user.get('id')),
            "employee": False,
            "restaurants": []
        }

        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_405_METHOD_NOT_ALLOWED
        }

        responses = create_responses(self, PROFILES_URL, data)
        check_responses(self, responses, status_codes)

    def test_profile_update(self):
        data = {
            "employee": True
        }

        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_200_OK
        }

        responses = update_responses(self, self.PROFILE_URL, data)
        check_responses(self, responses, status_codes)

    def test_profile_delete(self):
        status_codes = {
            'anonymous': status.HTTP_403_FORBIDDEN,
            'user': status.HTTP_403_FORBIDDEN,
            'admin': status.HTTP_405_METHOD_NOT_ALLOWED
        }

        responses = delete_responses(self, self.PROFILE_URL)
        check_responses(self, responses, status_codes)


def check_responses(instance, responses, status_codes):
    instance.assertEqual(responses['anonymous'].status_code,
                         status_codes['anonymous'])
    instance.assertEqual(responses['user'].status_code, status_codes['user'])
    instance.assertEqual(responses['admin'].status_code, status_codes['admin'])


def get_responses(instance, url):
    return {
        'anonymous': client.get(url),
        'user': instance.user_client.get(url),
        'admin': instance.admin_client.get(url)
    }


def create_responses(instance, url, data):
    return {
        'anonymous': client.post(url, data),
        'user': instance.user_client.post(url, data),
        'admin': instance.admin_client.post(url, data)
    }


def update_responses(instance, url, data,
                     field_name_to_replace_with_dynamic_data=None):
    if field_name_to_replace_with_dynamic_data:
        return {
            'anonymous': client.patch(url, {**data, **{
                field_name_to_replace_with_dynamic_data: uuid.uuid4().hex
            }}),
            'user': instance.user_client.patch(url, {**data, **{
                field_name_to_replace_with_dynamic_data: uuid.uuid4().hex
            }}),
            'admin': instance.admin_client.patch(url, {**data, **{
                field_name_to_replace_with_dynamic_data: uuid.uuid4().hex
            }})
        }
    return {
        'anonymous': client.patch(url, data),
        'user': instance.user_client.patch(url, data),
        'admin': instance.admin_client.patch(url, data)
    }


def delete_responses(instance, url):
    return {
        'anonymous': client.delete(url),
        'user': instance.user_client.delete(url),
        'admin': instance.admin_client.delete(url)
    }
