from django.urls import path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    BlogViewSet,
    CommentViewSet,
    ReplyViewSet,
    LikeViewSet,
    ReactionViewSet,
    TagViewSet,
)

router = routers.DefaultRouter()

router.register(r"category", CategoryViewSet, basename="category")
router.register(r"blog", BlogViewSet, basename="blog")
router.register(r"comment", CommentViewSet, basename="comment")
router.register(r"reply", ReplyViewSet, basename="reply")
router.register(r"like", LikeViewSet, basename="like")
router.register(r"reaction", ReactionViewSet, basename="reaction")
router.register(r"tag", TagViewSet, basename="tag")

custom_urlpatterns = [
    path(
        "blog/author/<str:username>/",
        BlogViewSet.as_view({"get": "list"}),
        name="blog-list-of-author",
    ),
    path(
        "comment/author/<str:username>/",
        CommentViewSet.as_view({"get": "list"}),
        name="comment-list-of-author",
    ),
    path(
        "reply/author/<str:username>/",
        ReplyViewSet.as_view({"get": "list"}),
        name="comment-list-of-author",
    ),
    path(
        "like/author/",
        LikeViewSet.as_view({"get": "list"}),
        name="comment-list-of-author",
    ),
    path(
        "reaction/author/",
        ReactionViewSet.as_view({"get": "list"}),
        name="comment-list-of-author",
    ),
]

urlpatterns = router.urls + custom_urlpatterns
