from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .filters import CategoryFilter
from .models import Category, Blog, Comment, Reply, Like, Reaction, Tag
from .pagination import CategoryPageNumberPagination, BlogsPageNumberPagination
from .permissions import IsAuthorOrAdmin
from .serializers import (
    CategorySerializer,
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
    ReactionForUserSerializer, TagCreateSerializer,
)

User = get_user_model()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    authentication_classes = [TokenAuthentication]
    filter_backends = [CategoryFilter]
    # filterset_class = CategoryFilter
    # filter_backends = [CategoryFilter]
    search_fields = ["name", "id"]
    pagination_class = CategoryPageNumberPagination

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


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

    # def get_permissions(self):
    #     # Grants permissions to POST, GET for authenticated users
    #     if self.action in ["list", "create"]:
    #         permission_classes = [IsAuthenticated]
    #     # Grants specific permissions for authors and admins
    #     else:
    #         permission_classes = [IsAuthorOrAdmin]
    #     return [permission() for permission in permission_classes]


# class BlogUserViewSet(viewsets.ModelViewSet):
#     serializer_class = BlogSerializer
#     queryset = Blog.objects.all()
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthorOrAdmin]
#
#     # def list(self, request, *args, **kwargs):
#     #     username = self.request.user
#     #     print(username)
#     #     return super().list(request, *args, **kwargs)
#
#     # Filtering against the current user
#     def get_queryset(self):
#         # Filtering against the current user
#
#         username = self.request.user
#         print(username)
#         return Blog.objects.filter(author__username=username)

# Filtering against queryset parameters

# username = self.kwargs["username"]
# return Blog.objects.filter(author__username=username)

#
# user_blogs = BlogUserViewSet.as_view({"get": "list"})
# user_blog_detail = BlogUserViewSet.as_view({"get": "retrieve"})


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

    # def get_serializer_class(self):
    #     if self.request.method == "POST":
    #         return TagCreateSerializer
    #     return super().get_serializer_class()