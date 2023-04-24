from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from accounts.factories import CustomUserFactory
from blogs.factories import CategoryFactory
from blogs.models import Category
from blogs.serializers import CategorySerializer


class CategoryViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.users = CustomUserFactory.create_batch(3)
        self.admin = self.users[0]
        self.admin.is_staff = True
        self.admin.save()
        self.user = self.users[1]

        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user)

        self.categories = CategoryFactory.create_batch(10)
        self.category = self.categories[0]

        self.url = reverse("category-list")
        self.detail_url = reverse("category-detail", kwargs={"pk": self.category.pk})

    def _generate_post_data(self):
        new_category = CategoryFactory.build()
        post_data = {"name": new_category.name}
        return post_data

    def _generate_invalid_post_data(self):
        existing_category = self.category
        post_data = {"name": existing_category.name}
        return post_data

    def _generate_invalid_put_patch_data(self):
        existing_category = self.categories[2]
        post_data = {"name": existing_category.name}
        return post_data

    def test_get_list_categories_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = CategorySerializer(self.categories, many=True)
        self.assertEqual(response.data["results"], serializer.data[:5])

    def test_get_list_categories_as_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = CategorySerializer(self.categories, many=True)
        self.assertEqual(response.data["results"], serializer.data[:5])

    def test_get_list_category_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_category_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = CategorySerializer(self.category)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_category_as_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = CategorySerializer(self.category)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_category_requires_authentication(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = self._generate_post_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name=response.data["name"]).exists())

    def test_create_category_validated_data(self):
        self.client.force_authenticate(self.admin)
        data = self._generate_invalid_post_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0], "category with this name already exists."
        )

    def test_create_category_requires_permission(self):
        self.client.force_authenticate(self.user)
        data = self._generate_post_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_requires_authentication(self):
        data = self._generate_post_data()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_category_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = self._generate_post_data()
        response = self.client.put(self.detail_url, data)
        self.category.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.category.name)

        response = self.client.patch(self.detail_url, data)
        self.categories[0].refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.category.name)

    def test_update_category_validate_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token}")
        data = self._generate_invalid_put_patch_data()
        response = self.client.put(self.detail_url, data)
        self.category.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0], "category with this name already exists."
        )

        response = self.client.patch(self.detail_url, data)
        self.categories[0].refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["name"][0], "category with this name already exists."
        )

    def test_update_category_requires_permission(self):
        self.client.force_authenticate(self.user)
        data = self._generate_post_data()
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    #
    def test_update_category_requires_authentication(self):
        category_url = f"{self.url}{self.categories[0].pk}/"
        data = {"name": "Updated Category Name"}
        response = self.client.put(category_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_category_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_delete_category_requires_permission(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category_requires_authentication(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
