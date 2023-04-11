from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from accounts.factories import CustomUserFactory
from accounts.models import CustomUser
from blogs.factories import CategoryFactory, BlogFactory


class BlogViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = CustomUser.objects.create_superuser(
            username="admin", password="admin"
        )
        self.user = CustomUserFactory.create()
        self.author = CustomUserFactory.create()

        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user)
        self.author_token = Token.objects.create(user=self.author)

        # self.users = CustomUserFactory.create_batch(20)

        self.category1 = CategoryFactory.create()
        self.category2 = CategoryFactory.create()

        self.blog1 = BlogFactory(author=self.author, category=self.category1)
        self.blog2 = BlogFactory(author=self.user, category=self.category2)

        self.url = reverse("blog-list")
        self.blog1_url = f"{self.url}{self.blog1.pk}/"

    def test_blog_list_as_authenticated_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        blog1_data = results[0]
        self.assertEqual(blog1_data['id'], self.blog1.pk)
        self.assertEqual(blog1_data['title'], self.blog1.title)

    # def test_blog_list_as_authenticated_admin(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    # def test_blog_list_requires_authentication(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    # def test_blog_retrieve_as_admin(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
    #     response = self.client.get(self.blog1_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    # def test_blog_retrieve_as_author(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
    #     response = self.client.get(self.blog1_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    # def test_blog_retrieve_as_user(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
    #     response = self.client.get(self.blog1_url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    # def test_blog_delete_as_user_requires_permission(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
    #     response = self.client.delete(self.blog1_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    # def test_blog_delete_as_author(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
    #     response = self.client.delete(self.blog1_url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #
    # def test_blog_delete_as_admir(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
    #     response = self.client.delete(self.blog1_url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #
    # def test_create_blog_as_authenticated_user(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
    #     data = {
    #         "author": self.author.id,
    #         "title": "New Blog",
    #         "description": "New blog description",
    #         "category": self.category1.id,
    #         "is_public": True,
    #     }
    #     response = self.client.post(self.url, data=data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_create_blog_as_authenticated_admin(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
    #     data = {
    #         "author": self.author.id,
    #         "title": "New Blog",
    #         "description": "New blog description",
    #         "category": self.category1.id,
    #         "is_public": True,
    #     }
    #     response = self.client.post(self.url, data=data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_create_blog_as_authenticated_author(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
    #     data = {
    #         "author": self.author.id,
    #         "title": "New Blog",
    #         "description": "New blog description",
    #         "category": self.category1.id,
    #         "is_public": True,
    #     }
    #     response = self.client.post(self.url, data=data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_create_blog_requires_authentication(self):
    #     data = {
    #         "author": self.author.id,
    #         "title": "New Blog",
    #         "description": "New blog description",
    #         "category": self.category1.id,
    #         "is_public": True,
    #     }
    #     response = self.client.post(self.url, data=data)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    # def test_update_blog_as_admin(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
    #     data = {
    #         "author": self.author.id,
    #         "title": "Updated Blog",
    #         "description": "Updated blog description",
    #         "category": self.category1.id,
    #         "is_public": False,
    #     }
    #     response = self.client.put(self.blog1_url, data)
    #     self.blog1.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["title"], "Updated Blog")
    #
    #     data = {"title": "New Title"}
    #     response = self.client.patch(self.blog1_url, data)
    #     self.blog1.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["title"], "New Title")
    #
    # def test_update_blog_as_author(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
    #     data = {
    #         "author": self.author.id,
    #         "title": "Updated Blog",
    #         "description": "Updated blog description",
    #         "category": self.category1.id,
    #         "is_public": False,
    #     }
    #     response = self.client.put(self.blog1_url, data)
    #     self.blog1.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["title"], "Updated Blog")
    #
    #     data = {"title": "New Title"}
    #     response = self.client.patch(self.blog1_url, data)
    #     self.blog1.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["title"], "New Title")
    #
    # def test_update_blog_requires_permission(self):
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
    #     data = {
    #         "author": self.author.id,
    #         "title": "Updated Blog",
    #         "description": "Updated blog description",
    #         "category": self.category1.id,
    #         "is_public": False,
    #     }
    #     response = self.client.put(self.blog1_url, data)
    #     self.blog1.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     data = {"title": "New Title"}
    #     response = self.client.patch(self.blog1_url, data)
    #     self.blog1.refresh_from_db()
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
