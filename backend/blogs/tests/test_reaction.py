from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from accounts.factories import CustomUserFactory
from blogs.factories import (
    ReactionFactory,
    BlogFactory,
    CommentFactory,
    CategoryFactory,
)
from blogs.models import Reaction
from blogs.serializers import ReactionSerializer


class ReactionViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUserFactory(username="admin")
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.author = CustomUserFactory(username="author")
        self.user = CustomUserFactory(username="user")

        # Create Tokens
        self.admin_token = Token.objects.create(user=self.admin)
        self.author_token = Token.objects.create(user=self.author)
        self.user_token = Token.objects.create(user=self.user)

        # Create Data
        self.category = CategoryFactory.create()
        self.blog = BlogFactory.create(category=self.category, author=self.author)
        self.comments = CommentFactory.create_batch(3, blog=self.blog, author=self.user)
        self.reactions = ReactionFactory.create_batch(
            10, blog=self.blog, comment=self.comments[0], author=self.author
        )
        self.reaction = self.reactions[0]
        self.reaction.author = self.author
        self.reaction.save()

        # url
        self.url = reverse("reaction-list")
        self.retrieve_url = reverse("reaction-detail", kwargs={"pk": self.reaction.pk})
        self.retrieve_with_username_url = (
            f"{self.url}author/?username={self.author.username}"
        )

    def test_list_reaction_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.reactions))

    def test_list_reaction_as_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.reactions))

    def test_list_reaction_by_username(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.retrieve_with_username_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["author"], self.author.pk)

    def test_retrieve_reaction_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.reaction.pk)

    def test_retrieve_reaction_by_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.reaction.pk)

    def test_retrieve_reaction_requires_authentication(self):
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_reaction_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {
            "blog": self.blog.pk,
            "comment": self.comments[0].pk,
            "reaction_type": "Like",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_reaction = Reaction.objects.get(pk=response.data["id"])
        serializer = ReactionSerializer(created_reaction, many=False)
        self.assertEqual(response.data, serializer.data)

    def test_create_reaction_by_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        data = {
            "blog": self.blog.pk,
            "comment": self.comments[0].pk,
            "reaction_type": "Like",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_reaction = Reaction.objects.get(pk=response.data["id"])
        serializer = ReactionSerializer(created_reaction, many=False)
        self.assertEqual(response.data, serializer.data)

    def test_create_reaction_requires_authentication(self):
        data = {
            "blog": self.blog.pk,
            "comment": self.comments[0].pk,
            "reaction_type": "Like",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_reaction_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {
            "blog": self.blog.pk,
            "comment": self.comments[0].pk,
            "reaction_type": "Angry",
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["reaction_type"], "Angry")

        data = {"reaction_type": "Haha"}
        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["reaction_type"], "Haha")

    def test_update_reaction_by_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        data = {
            "blog": self.blog.pk,
            "comment": self.comments[0].pk,
            "reaction_type": "Angry",
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["reaction_type"], "Angry")

        data = {"reaction_type": "Love"}
        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["reaction_type"], "Love")

    def test_updated_reaction_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        data = {
            "blog": self.blog.pk,
            "comment": self.comments[0].pk,
            "reaction_type": "Angry",
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data = {"reaction_type": "Love"}
        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_updated_reaction_requires_authentication(self):
        data = {
            "blog": self.blog.pk,
            "comment": self.comments[0].pk,
            "reaction_type": "Angry",
        }
        response = self.client.put(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        data = {"reaction_type": "Love"}
        response = self.client.patch(self.retrieve_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_reaction_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_delete_reaction_as_author(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.author_token}")
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_delete_reaction_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_reaction_requires_authentication(self):
        response = self.client.delete(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
