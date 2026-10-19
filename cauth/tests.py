from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
# Create your tests here.

BASE_URL = "/api/auth/"


class CreateUser(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        # send the request with the required data
        data = {"username": "hello", "password": "GoodOldPassword"}
        res = self.client.post(f"{BASE_URL}signup/", data=data, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(1, User.objects.count())


class LoginUser(TestCase):
    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(username="hello", password="GoodOldPassword")

    def test_create_user(self):
        # send the request with the required data
        data = {"username": "hello", "password": "GoodOldPassword"}
        res = self.client.post(f"{BASE_URL}login/", data=data, format="json")
        ans = res.json()
        user = User.objects.get(username="hello")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(ans["key"], Token.objects.get(user=user).key)
