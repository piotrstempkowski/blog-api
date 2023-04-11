from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Blog, Category, Comment, Reply, Like, Reaction, Tag

User = get_user_model()


class ReplyForUserSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    comment = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all())
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = [
            "author",
            "comment",
            "text",
            "created_at",
            "updated_at",
        ]

    def get_created_at(self, obj):
        local_created_at = obj.created_at.astimezone(timezone.utc)
        return local_created_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_updated_at(self, obj):
        local_updated_at = obj.updated_at.astimezone(timezone.utc)
        return local_updated_at.strftime("%Y-%m-%d %H:%M:%S")

    def validate_text(self, value):
        CURSE_WORDS = ["badword1", "badword2", "badword2"]
        words = value.lower().split()
        if any(word in CURSE_WORDS for word in words):
            raise serializers.ValidationError(
                "The text contains inappropriate language."
            )
        return value


class ReplayForCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = "__all__"


class BlogSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    posted_at = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "author",
            "category",
            "is_public",
            "posted_at",
            "slug",
        ]

    def get_len_blog_title(self, object):
        return len(object.title)

    def get_posted_at(self, obj):
        local_posted_at = obj.posted_at.astimezone(timezone.utc)
        return local_posted_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_author_username(self, obj):
        return obj.author.username

    def get_category_name(self, obj):
        return obj.category.name


class BlogForCategorySerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(source="author.username", read_only=True)

    class Meta:
        model = Blog
        fields = ["id", "title", "description", "posted_at", "author"]


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    blogs = BlogForCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = "__all__"


class BlogForUserSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(
        source="category.name", read_only=True
    )
    posted_at = serializers.SerializerMethodField()
    len_blog_title = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            "id",
            "category_name",
            "title",
            "description",
            "is_public",
            "posted_at",
            "len_blog_title",
        ]

    def get_posted_at(self, obj):
        local_posted_at = obj.posted_at.astimezone(timezone.utc)
        return local_posted_at

    def get_len_blog_title(self, object):
        return len(object.title)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    blog = serializers.PrimaryKeyRelatedField(queryset=Blog.objects.all())
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "author",
            "blog",
            "text",
            "created_at",
        ]

    def get_created_at(self, obj):
        local_created_at = obj.created_at.astimezone(timezone.utc)
        return local_created_at.strftime("%Y-%m-%d %H:%M:%S %Z")

    def validate_text(self, value):
        CURSE_WORDS = ["badword1", "badword2", "badword2"]
        words = value.lower().split()
        if any(word in CURSE_WORDS for word in words):
            raise serializers.ValidationError(
                "The text contains inappropriate language."
            )
        return value


class ReactionSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    blog = serializers.PrimaryKeyRelatedField(queryset=Blog.objects.all())
    comment = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all())

    class Meta:
        model = Reaction
        fields = [
            "id",
            "author",
            "blog",
            "comment",
            "reaction_type",
            "given_at",
        ]


class ReactionForUserSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    blog = BlogForUserSerializer()
    comment = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all())

    class Meta:
        model = Reaction
        fields = [
            "author",
            "blog",
            "comment",
            "reaction_type",
            "given_at",
        ]


class CommentForUserSerializer(serializers.ModelSerializer):
    author_name = serializers.StringRelatedField(source="author.username")
    blog_title = serializers.StringRelatedField(source="blog.title")
    blog = BlogForUserSerializer()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    replies = ReplayForCommentSerializer(many=True, read_only=True)
    reactions = ReactionForUserSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            "author_name",
            "blog_title",
            "blog",
            "text",
            "created_at",
            "updated_at",
            "reactions",
            "replies",
        ]
        read_only_fields = ["created_at, updated_at"]

    def get_created_at(self, obj):
        local_created_at = obj.created_at.astimezone(timezone.utc)
        return local_created_at.strftime("%Y-%m-%d %H:%M:%S %Z")

    def get_updated_at(self, obj):
        local_created_at = obj.created_at.astimezone(timezone.utc)
        return local_created_at.strftime("%Y-%m-%d %H:%M:%S %Z")


class ReplySerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    comment = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all())
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = [
            "id",
            "author",
            "comment",
            "text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at, updated_at"]

    def get_created_at(self, obj):
        local_created_at = obj.created_at.astimezone(timezone.utc)
        return local_created_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_updated_at(self, obj):
        local_updated_at = obj.updated_at.astimezone(timezone.utc)
        return local_updated_at.strftime("%Y-%m-%d %H:%M:%S")

    def validate_text(self, value):
        CURSE_WORDS = ["badword1", "badword2", "badword2"]
        words = value.lower().split()
        if any(word in CURSE_WORDS for word in words):
            raise serializers.ValidationError(
                "The text contains inappropriate language."
            )
        return value


class LikeSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    blog = serializers.PrimaryKeyRelatedField(queryset=Blog.objects.all())
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Like
        fields = ["author", "blog", "created_at"]

    def get_created_at(self, obj):
        local_created_at = obj.created_at.astimezone(timezone.utc)
        return local_created_at.strftime("%Y-%m-%d %H:%M:%S")


class LikeForUserSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    blog = BlogForUserSerializer()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Like
        fields = [
            "author",
            "blog",
            "created_at",
        ]

    def get_created_at(self, obj):
        local_created_at = obj.created_at.astimezone(timezone.utc)
        return local_created_at.strftime("%Y-%m-%d %H:%M:%S")


class TagSerializer(serializers.ModelSerializer):
    blogs = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Blog.objects.all(),
    )
    comments = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Comment.objects.all(),
    )

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "blogs",
            "comments",
        ]

    def create(self, validated_data):
        blog_data = validated_data.pop("blogs")
        comments_data = validated_data.pop("comments")
        tag = Tag.objects.create(**validated_data)

        for blog in blog_data:
            tag.blogs.add(blog)

        for comment in comments_data:
            tag.comments.add(comment)

        tag.save()
        return tag


class TagCreateSerializer(serializers.ModelSerializer):
    blogs = BlogSerializer(many=True)
    comments = CommentSerializer(many=True)

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "blogs",
            "comments",
        ]

    def create(self, validated_data):
        blogs_data = validated_data.pop("blogs")
        comments_data = validated_data.pop("comments")
        tag = Tag.objects.create(**validated_data)

        for blog in blogs_data:
            author = blog.pop("author")
            category = blog.pop("category")
            blog = Blog.objects.create(author=author, category=category)
            tag.blogs.add(blog)

        for comment in comments_data:
            author = self.context["request"].user
            blog = comment.pop("blog")
            comment = Comment.objects.create(author=author, blog=blog)
            tag.comments.add(comment)

        tag.save()
        return tag
