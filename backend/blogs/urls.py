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

router_category = routers.DefaultRouter()
router_blogs = routers.SimpleRouter()
router_comment = routers.SimpleRouter()
router_reply = routers.SimpleRouter()
router_like = routers.SimpleRouter()
router_reaction = routers.SimpleRouter()
router_tag = routers.SimpleRouter()

router_category.register(r"category", CategoryViewSet, basename="category")
router_blogs.register(r"blog", BlogViewSet, basename="blog")
router_comment.register(r"comment", CommentViewSet, basename="comment")
router_reply.register(r"reply", ReplyViewSet, basename="reply")
router_like.register(r"like", LikeViewSet, basename="like")
router_reaction.register(r"reaction", ReactionViewSet, basename="reaction")
router_tag.register(r"tag", TagViewSet, basename="tag")

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

urlpatterns = (
    custom_urlpatterns
    + router_category.urls
    + router_blogs.urls
    + router_comment.urls
    + router_reply.urls
    + router_like.urls
    + router_reaction.urls
    + router_tag.urls
)
