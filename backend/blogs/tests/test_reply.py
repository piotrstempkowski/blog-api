from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from accounts.factories import CustomUserFactory
from blogs.factories import ReplyFactory, CommentFactory, BlogFactory, CategoryFactory
from blogs.models import Reply
from blogs.serializers import ReplySerializer


class ReplyViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create data
        self.users = CustomUserFactory.create_batch(10)

        self.user = self.users[0]
        self.author = self.users[1]
        self.admin = self.users[2]
        self.admin.is_superuser = True
        self.admin.is_staff = True
        self.admin.save()
        self.category = CategoryFactory.create()
        self.blog = BlogFactory.create(category=self.category, author=self.author)
        self.comment = CommentFactory.create(author=self.author, blog=self.blog)
        self.replies = ReplyFactory.create_batch(
            10, author=self.user, comment=self.comment
        )
        self.reply = self.replies[0]
        self.reply.author = self.author
        self.reply.save()
        # Create Tokens
        self.admin_token = Token.objects.create(user=self.admin)
        self.author_token = Token.objects.create(user=self.author)
        self.user_token = Token.objects.create(user=self.user)

        # url
        self.url = reverse("reply-list")
        self.retrieve_url = reverse("reply-detail", kwargs={"pk": self.reply.pk})

    def test_list_reply_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ReplySerializer(self.replies, many=True)
        response_data_sorted = sorted(response.data, key=lambda x: x["id"])
        serializer_data_sorted = sorted(serializer.data, key=lambda x: x["id"])

        self.assertEqual(response_data_sorted, serializer_data_sorted)

    def test_list_reply_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ReplySerializer(self.replies, many=True)
        response_data_sorted = sorted(response.data, key=lambda x: x["id"])
        serializer_data_sorted = sorted(serializer.data, key=lambda x: x["id"])

        self.assertEqual(response_data_sorted, serializer_data_sorted)

    def test_list_reply_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_reply_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ReplySerializer(self.reply)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_reply_as_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ReplySerializer(self.reply)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_reply_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ReplySerializer(self.reply)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_reply_requires_authentication(self):
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_reply_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")

        data = {
            "comment": self.comment.pk,
            "text": "test text",
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reply_instance = Reply.objects.get(id=response.data["id"])
        serializer = ReplySerializer(reply_instance)
        self.assertEqual(response.data, serializer.data)

    def test_create_reply_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        data = {
            "comment": self.comment.pk,
            "text": "test text",
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reply_instance = Reply.objects.get(id=response.data["id"])
        serializer = ReplySerializer(reply_instance)
        self.assertEqual(response.data, serializer.data)

    def test_reply_requires_authentication(self):
        data = {
            "comment": self.comment.pk,
            "text": "test text",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reply_validate_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        data = {"comment": self.comment.pk, "text": "badword1, badword2"}
        response = self.client.post(self.url, data)
        self.assertEqual(
            response.data["text"][0], "The text contains inappropriate language."
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_reply_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {
            "comment": self.comment.pk,
            "text": "updated text",
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "updated text")

        data = {
            "text": "updated text",
        }
        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"], "updated text")

    def test_update_reply_as_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        data = {
            "comment": self.comment.pk,
            "text": "updated text",
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["comment"], self.comment.pk)
        data = {"comment": self.comment.pk}
        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["comment"], self.comment.pk)

    def test_update_reply_validate_text(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {
            "comment": self.comment.pk,
            "text": "badword1 badword2",
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["text"][0], "The text contains inappropriate language."
        )

        data = {
            "text": "badword1 badword2",
        }
        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["text"][0], "The text contains inappropriate language."
        )

    def test_update_reply_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        data = {
            "comment": self.comment.pk,
            "text": "updated text",
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data = {"comment": self.comment.pk}
        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_reply_requires_authentication(self):
        data = {
            "comment": self.comment.pk,
            "text": "updated text",
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {"comment": self.comment.pk}
        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_reply_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_delete_reply_as_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_delete_reply_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_reply_requires_authentication(self):
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
