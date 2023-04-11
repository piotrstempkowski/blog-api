from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from accounts.factories import CustomUserFactory
from blogs.factories import TagFactory, BlogFactory, CommentFactory, CategoryFactory
from blogs.models import Tag
from blogs.serializers import TagSerializer


class TagViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # create users
        self.users = CustomUserFactory.create_batch(10)
        self.admin = self.users[0]
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.user = self.users[1]
        self.user.save()

        # create data
        self.category = CategoryFactory.create()
        self.blogs = BlogFactory.create_batch(
            2, author=self.user, category=self.category
        )
        self.blog = self.blogs[0]
        self.comments = CommentFactory.create_batch(
            10, author=self.user, blog=self.blog
        )
        self.tags = TagFactory.create_batch(10)
        for tag in self.tags:
            tag.blogs.set(self.blogs)
            tag.comments.set(self.comments)
        self.tag = self.tags[0]
        self.tag.save()

        # create tokes
        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user)

        # urls
        self.url = reverse("tag-list")
        self.url_retrieve = reverse(("tag-detail"), kwargs={"pk": self.tag.pk})

    def test_tag_list_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.tags))

    def test_tag_list_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_tag_list_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tag_retrieve_list_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.url_retrieve)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = Tag.objects.get(id=self.tag.id)
        serializers = TagSerializer(expected_data)
        self.assertEqual(response.data, serializers.data)

    def test_tag_retrieve_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.url_retrieve)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_tag_retrieve_requires_authentication(self):
        response = self.client.get(self.url_retrieve)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tag_create_tag_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {
            "name": "Example tag",
            "blogs": [self.blogs[1].pk],
            "comments": [self.comments[2].pk],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Example tag")

    def test_tag_create_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        data = {
            "name": "Example tag",
            "blogs": [self.blogs[1].pk],
            "comments": [self.comments[2].pk],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_tag_create_requires_authentication(self):
        data = {
            "name": "Example tag",
            "blogs": [self.blogs[1].pk],
            "comments": [self.comments[2].pk],
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {
            "name": "Updated tag",
            "blogs": [self.blogs[1].pk],
            "comments": [self.comments[2].pk],
        }
        response = self.client.put(self.url_retrieve, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(response.data["name"], "Updated tag")

        data = {"blogs": [self.blogs[1].pk]}
        response = self.client.patch(self.url_retrieve, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["blogs"], [self.blogs[1].pk])
        print(response.data)

    def test_update_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        data = {
            "name": "Updated tag",
            "blogs": [self.blogs[1].pk],
            "comments": [self.comments[2].pk],
        }
        response = self.client.put(self.url_retrieve, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data = {"blogs": [self.blogs[1].pk]}
        response = self.client.patch(self.url_retrieve, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_requires_authentication(self):
        data = {
            "name": "Updated tag",
            "blogs": [self.blogs[1].pk],
            "comments": [self.comments[2].pk],
        }
        response = self.client.put(self.url_retrieve, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {"blogs": [self.blogs[1].pk]}
        response = self.client.patch(self.url_retrieve, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_tag_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.delete(self.url_retrieve)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_delete_Tag_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.delete(self.url_retrieve)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_tag_requires_authentication(self):
        response = self.client.delete(self.url_retrieve)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
