from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAdminUser

from .filters import CategoryFilter
from .models import Category, Blog, Comment, Reply, Like, Reaction, Tag
from .pagination import CategoryPageNumberPagination, BlogsPageNumberPagination
from .permissions import StaffAllReadOnlyUser, IsAuthorOrAdmin
from .serializers import (
    CategorySerializer,
    CategoryCreateSerializer,
    BlogSerializer,
    CommentSerializer,
    BlogForUserSerializer,
    ReplySerializer,
    LikeSerializer,
    ReactionSerializer,
    TagSerializer,
    CommentForUserSerializer,
    ReplyForUserSerializer,
    LikeForUserSerializer,
    ReactionForUserSerializer,
)

User = get_user_model()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    authentication_classes = [TokenAuthentication]
    filter_backends = [CategoryFilter, OrderingFilter]
    ordering = ["id"]
    search_fields = ["name", "id"]
    pagination_class = CategoryPageNumberPagination
    permission_classes = [StaffAllReadOnlyUser]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return super().get_serializer_class()
        return CategoryCreateSerializer


class BlogViewSet(viewsets.ModelViewSet):
    serializer_class = BlogSerializer
    queryset = Blog.objects.all()
    authentication_classes = [TokenAuthentication]
    pagination_class = BlogsPageNumberPagination

    permission_classes = [IsAuthorOrAdmin]

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return BlogForUserSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        username = self.kwargs.get("username")
        if username:
            try:
                return Blog.objects.filter(author__username=username)
            except User.DoesNotExist:
                pass
        return super().get_queryset()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorOrAdmin]

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_queryset(self):
        username = self.kwargs.get("username")
        queryset = Comment.objects.all()

        if username:
            try:
                queryset = Comment.objects.filter(author__username=username)
            except User.DoesNotExist:
                pass
        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET" and self.kwargs.get("username"):
            return CommentForUserSerializer
        return super().get_serializer_class()


class ReplyViewSet(viewsets.ModelViewSet):
    serializer_class = ReplySerializer
    queryset = Reply.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorOrAdmin]

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_queryset(self):
        username = self.kwargs.get("username")
        queryset = Reply.objects.all()

        if username:
            try:
                queryset = Reply.objects.filter(author_username=username)
            except User.DoesNotExist:
                pass
        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET" and self.kwargs.get("username"):
            return ReplyForUserSerializer
        return super().get_serializer_class()


class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorOrAdmin]

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Like.objects.all()
        username = self.kwargs.get("username")
        if username:
            queryset = queryset.filter(author_username=username)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET" and self.kwargs.get("username"):
            return LikeForUserSerializer
        return super().get_serializer_class()


class ReactionViewSet(viewsets.ModelViewSet):
    serializer_class = ReactionSerializer
    queryset = Reaction.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorOrAdmin]

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Reaction.objects.all()
        username = self.request.query_params.get("username")
        if username:
            return queryset.filter(author__username=username)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "GET" and self.request.query_params.get("username"):
            return ReactionForUserSerializer
        return super().get_serializer_class()


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]
