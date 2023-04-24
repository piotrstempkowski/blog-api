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
        self.users = CustomUserFactory.create_batch(3)
        self.admin = self.users[0]
        self.admin.is_staff = True
        self.admin.save()
        self.user = self.users[1]
        self.another_user = self.users[2]
        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user)
        self.another_user_token = Token.objects.create(user=self.another_user)
        self.url = reverse("user-list")
        self.url_detail = reverse("user-detail", kwargs={"pk": self.user.pk})

    def _generate_post_or_put_data(self):
        new_user = (
            CustomUserFactory.build()
        )  # Use `build` instead of `create` to avoid saving the instance to the database
        post_data = {
            "username": new_user.username,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "password": "testpass123",
        }
        return post_data

    def _generate_patch_data(self):
        new_user = (
            CustomUserFactory.build()
        )  # Use `build` instead of `create` to avoid saving the instance to the database
        patch_data = {
            "email": new_user.email,
            "password": "testpass123",
        }
        return patch_data

    def test_get_list_users_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_requires_permission(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_list_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serialized_user = UserSerializer(self.user).data
        self.assertEqual(response.data, serialized_user)
        self.assertEqual(response.data["username"], self.user.username)

    def test_retrieve_user_as_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_user_requires_permission(self):
        self.client.force_authenticate(self.another_user)
        response = self.client.get(self.url_detail)
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

    def test_create_user_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        data = self._generate_post_or_put_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user_username = response.data["username"]
        self.assertTrue(
            CustomUser.objects.filter(username=created_user_username).exists()
        )
        created_user_password = response.data["password"]
        self.assertTrue(check_password("testpass123", created_user_password))

    def test_create_user_requires_permission(self):
        self.client.force_authenticate(self.user)
        data = self._generate_post_or_put_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_requires_authentication(self):
        data = self._generate_post_or_put_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        put_data = self._generate_post_or_put_data()
        response = self.client.put(self.url_detail, put_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        updated_email = response.data["email"]
        updated_password = response.data["password"]
        updated_user = self.user
        self.assertEqual(updated_user, self.user)
        self.assertEqual(updated_password, self.user.password)
        self.assertEqual(updated_email, self.user.email)

        patch_data = self._generate_patch_data()
        response = self.client.patch(self.url_detail, patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        updated_email = response.data["email"]
        updated_password = response.data["password"]
        self.assertEqual(updated_user, self.user)
        self.assertEqual(updated_password, self.user.password)
        self.assertEqual(updated_email, self.user.email)

    def test_update_user_as_user(self):
        self.client.force_authenticate(self.user)
        put_data = self._generate_post_or_put_data()
        response = self.client.put(self.url_detail, put_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        updated_email = response.data["email"]
        updated_password = response.data["password"]
        updated_user = self.user
        self.assertEqual(updated_user, self.user)
        self.assertEqual(updated_password, self.user.password)
        self.assertEqual(updated_email, self.user.email)

        patch_data = self._generate_patch_data()
        response = self.client.patch(self.url_detail, patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        updated_password = response.data["password"]
        self.assertEqual(updated_user, self.user)
        self.assertEqual(updated_password, self.user.password)
        self.assertEqual(updated_user.email, self.user.email)

    def test_update_user_requires_permissions(self):
        random_user = CustomUserFactory.create()
        random_user_token = Token.objects.create(user=random_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {random_user_token}")
        data = self._generate_post_or_put_data()
        response = self.client.patch(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_requires_authentication(self):
        data = self._generate_post_or_put_data()
        response = self.client.patch(self.url_detail, data)
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
