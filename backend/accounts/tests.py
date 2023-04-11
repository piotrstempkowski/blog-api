from django.contrib.auth.hashers import check_password
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from .factories import CustomUserFactory, CustomUser
from .serializers import UserSerializer


class UserViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_superuser(
            username="admin", password="admin"
        )
        self.user = CustomUserFactory.create()
        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user)
        self.url = reverse("user-list")
        self.url_detail = reverse("user-detail", kwargs={"pk": self.user.pk})

    def test_create_user_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        new_user = (
            CustomUserFactory.build()
        )  # Use `build` instead of `create` to avoid saving the instance to the database
        data = {
            "username": new_user.username,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "password": "testpass123",
        }
        response = self.client.post(self.url, data)
        print(response.data["password"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(username=new_user.username).exists())
        # Retrieve the created user from database
        created_user = CustomUser.objects.get(username=new_user.username)

        # Check if password was saved as a hashed value
        self.assertTrue(check_password("testpass123", created_user.password))

    def test_create_user_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token.key}")
        new_user = CustomUserFactory.build()
        data = {
            "username": new_user.username,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "password": "testpass123",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_requires_authentication(self):
        new_user = CustomUserFactory.build()
        data = {
            "username": new_user.username,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "password": "testpass123",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token.key}")
        data = {
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "password": "updatedpassword",
        }
        response = self.client.patch(f"{self.url}{self.user.pk}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("updatedpassword"))

    def test_update_user_requires_permissions(self):
        random_user = CustomUserFactory.create()
        random_user_token = Token.objects.create(user=random_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {random_user_token}")
        data = {
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "password": "updatedpassword",
        }
        response = self.client.patch(f"{self.url}{self.user.pk}/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_requires_authentication(self):
        data = {
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "password": "updatedpassword",
        }
        response = self.client.patch(f"{self.url}{self.user.pk}/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.delete(f"{self.url}{self.user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertFalse(self.user.has_usable_password())

    def test_delete_user_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.delete(f"{self.url}{self.user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_requires_authentication(self):
        response = self.client.delete(f"{self.url}{self.user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serialized_user = UserSerializer(self.user).data
        self.assertEqual(response.data, serialized_user)
        self.assertEqual(response.data["username"], self.user.username)

    def test_retrieve_user_requires_permission(self):
        example_user = CustomUserFactory.create()
        example_user_url = reverse("user-detail", kwargs={"pk": example_user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(example_user_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_user_requires_authentication(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_by_himself(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serialized_user = UserSerializer(self.user).data
        self.assertEqual(response.data, serialized_user)
        self.assertEqual(response.data["username"], self.user.username)
