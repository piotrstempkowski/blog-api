from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from accounts.factories import CustomUserFactory
from accounts.models import CustomUser
from blogs.factories import CategoryFactory
from blogs.models import Category
from blogs.serializers import CategorySerializer


class CategoryViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create admin and user
        self.admin = CustomUser.objects.create_superuser(
            username="admin", password="admin"
        )
        self.user = CustomUserFactory.create()

        # Generates token for authentication
        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user)

        # Create a test category
        self.categories = CategoryFactory.create_batch(10)

        # Get URL for the ViewSet
        self.url = reverse("category-list")

    def test_list_categories_as_authenticated_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(f"RESPONSE DATA CATEGORY '\n' {response.data}")

    def test_create_category_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = {"name": "Test Category"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name="Test Category").exists())

    def test_create_category_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        data = {"name": "Test Category"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_requires_authentication(self):
        data = {"name": "Test Category"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_category_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        category_url = f"{self.url}{self.categories[0].pk}/"
        data = {"name": "Updated Category Name"}
        response = self.client.put(category_url, data)
        self.categories[0].refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Category Name")

        response = self.client.patch(category_url, data)
        self.categories[0].refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Category Name")

    def test_update_category_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        category_url = f"{self.url}{self.categories[0].pk}/"
        data = {"name": "Updated Category Name"}
        response = self.client.put(category_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_category_requires_authentication(self):
        category_url = f"{self.url}{self.categories[0].pk}/"
        data = {"name": "Updated Category Name"}
        response = self.client.put(category_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_category_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        category_url = f"{self.url}{self.categories[0].pk}/"
        response = self.client.delete(category_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_category_requires_permission(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token.key}")
        category_url = f"{self.url}{self.categories[0].pk}/"
        response = self.client.delete(category_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category_requires_authentication(self):
        category_url = f"{self.url}{self.categories[0].pk}/"
        category_url = f"{self.url}{self.categories[0].pk}/"
        response = self.client.delete(category_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_categories_pagination(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Set the expected number of categories per page
        expected_page_size = 5

        # Check if the actual number of categories returned is equal to the expected page size
        self.assertEqual(len(response.data["results"]), expected_page_size)

        # Deserialize the response data
        deserialized_data = CategorySerializer(data=response.data["results"], many=True)
        deserialized_data.is_valid(raise_exception=True)

        # Verify that the deserialized data is in the initial categories list
        for category in deserialized_data.validated_data:
            self.assertIn(category["name"], [cat.name for cat in self.categories])