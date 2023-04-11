from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from accounts.factories import CustomUserFactory
from blogs.factories import LikeFactory, BlogFactory, CategoryFactory
from blogs.serializers import LikeSerializer


class LikeViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.users = CustomUserFactory.create_batch(10)
        self.admin = self.users[0]
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.author = self.users[1]
        self.author.save()
        self.user = self.users[2]
        self.user.save()

        # Create Tokens
        self.admin_token = Token.objects.create(user=self.admin)
        self.author_token = Token.objects.create(user=self.author)
        self.user_token = Token.objects.create(user=self.user)

        # Create Data
        self.category = CategoryFactory.create()
        self.blog = BlogFactory.create(category=self.category, author=self.author)
        self.blog1 = BlogFactory.create(category=self.category, author=self.author)
        self.likes = LikeFactory.create_batch(10, blog=self.blog, author=self.author)
        self.like = self.likes[0]
        self.like.author = self.author
        self.like.save()

        # create urls
        self.url = reverse("like-list")
        self.retrieve_url = reverse("like-detail", kwargs={"pk": self.like.pk})

    def test_like_list_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.likes))

    def test_like_list_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.likes))


    def test_like_list_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_like_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = LikeSerializer(self.like)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_like_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = LikeSerializer(self.like)
        self.assertEqual(response.data, serializer.data)

    def test_create_like_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {
            "blog": self.blog.pk
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["blog"], self.blog.pk)
        self.assertEqual(response.data["author"], self.admin.pk)

    def test_create_like_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        data = {
            "blog": self.blog.pk
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["blog"], self.blog.pk)
        self.assertEqual(response.data["author"], self.user.pk)

    def test_create_like_requires_authentication(self):
        data = {
            "blog": self.blog.pk
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_updated_like_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {
            "blog": self.blog1.pk
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["blog"], self.blog1.pk)

        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["blog"], self.blog1.pk)

    def test_updated_like_as_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        data = {
            "blog": self.blog1.pk
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["blog"], self.blog1.pk)

        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["blog"], self.blog1.pk)

    def test_updated_like_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        data = {
            "blog": self.blog1.pk
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_updated_like_requires_authentication(self):
        data = {
            "blog": self.blog1.pk
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_like_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_delete_like_as_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_delete_like_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_like_requires_authentication(self):
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
