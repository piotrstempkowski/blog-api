from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from accounts.factories import CustomUserFactory
from accounts.models import CustomUser
from blogs.factories import CommentFactory, BlogFactory, CategoryFactory
from blogs.models import Comment
from blogs.serializers import CommentSerializer, CommentForUserSerializer


class CommentViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = CustomUser.objects.create_superuser(
            username="admin", password="admin"
        )
        self.user = CustomUserFactory.create()
        self.author = CustomUserFactory.create()
        self.random_user = CustomUserFactory.create()

        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user)
        self.author_token = Token.objects.create(user=self.author)
        self.category = CategoryFactory.create()
        self.blog = BlogFactory.create(category=self.category, author=self.author)
        self.comments = CommentFactory.create_batch(
            10, blog=self.blog, author=self.author
        )
        self.url = reverse("comment-list")
        self.comment_url = f"{self.url}{self.comments[0].pk}/"

    def test_list_comment_as_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.comments))
        queryset = Comment.objects.filter(blog=self.blog)
        serializer = CommentSerializer(queryset, many=True)
        self.assertEqual(serializer.data, response.data)

    def test_list_comment_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_comments_by_username(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        url_with_username = f"{self.url}author/{self.author.username}/"
        response = self.client.get(url_with_username)
        print(f"url_with_username: {url_with_username}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = Comment.objects.filter(author=self.author)
        serializer = CommentForUserSerializer(expected_data, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_comment_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.comment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Get the expected comment and not expected
        expected_comment = self.comments[0]
        serializer = CommentSerializer(self.comments[0])
        self.assertEqual(serializer.data, response.data)

    def test_retrieve_comment_as_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        response = self.client.get(self.comment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_comment_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.comment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_comment_requires_authentication(self):
        response = self.client.get(self.comment_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {
            "blog": self.blog.pk,
            "text": "Test text",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(response.data["text"], "Test text")

    def test_create_comment_validate_text(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {
            "blog": self.blog.pk,
            "text": "badword1, badword2",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "The text contains inappropriate language.", response.data["text"]
        )

    def test_create_comment_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        data = {
            "blog": self.blog.pk,
            "text": "User test",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["text"], "User test")

    def test_update_comment_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {
            "blog": self.blog.pk,
            "text": "updated text",
        }
        response = self.client.put(self.comment_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "updated text")
        self.assertEqual(response.data["blog"], self.blog.pk)

        data = {"text": "patch text"}
        response = self.client.patch(self.comment_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "patch text")

    def test_update_comment_as_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        data = {
            "blog": self.blog.pk,
            "text": "updated text",
        }
        response = self.client.put(self.comment_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "updated text")
        self.assertEqual(response.data["blog"], self.blog.pk)

        data = {"text": "patch text"}
        response = self.client.patch(self.comment_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "patch text")

    def test_update_comment_requires_authentication(self):
        data = {
            "blog": self.blog.pk,
            "text": "updated text",
        }
        response = self.client.put(self.comment_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        data = {
            "blog": self.blog.pk,
            "text": "updated text",
        }
        response = self.client.put(self.comment_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data = {"text": "patch text"}
        response = self.client.patch(self.comment_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.delete(self.comment_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_comment_as_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        response = self.client.delete(self.comment_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_comment_requires_authentication(self):
        response = self.client.delete(self.comment_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_comment_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.delete(self.comment_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
