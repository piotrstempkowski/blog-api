from rest_framework import serializers

from blogs.models import Blog
from .models import CustomUser


class UserBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            "title",
            "description",
            "posted_at",
        ]


class UserSerializer(serializers.ModelSerializer):
    blogs = UserBlogSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        # exclude = ["password"]
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "last_login",
            "deleted",
            "blogs_amount",
            "blogs",
        ]


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "password")
        # extra_kwargs = {"password": {"write_only": True}}
