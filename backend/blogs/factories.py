import random
import string

import factory
from django.template.defaultfilters import slugify
from factory.django import DjangoModelFactory

from accounts.models import CustomUser
from .models import Category, Blog, Comment, Reply, Like, Reaction, Tag

CATEGORY_NAMES = [
    "Electronics",
    "Movies",
    "Songs",
    "Books",
    "Clothes",
    "Sports",
    "Science",
    "Physics",
    "Politics",
    "News",
]


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "password123")


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")


class BlogFactory(DjangoModelFactory):
    class Meta:
        model = Blog

    author = factory.Iterator(CustomUser.objects.all())
    # author = factory.SubFactory(CustomUserFactory)  # Change this line

    title = factory.Sequence(lambda n: f"Blog Title {n}")
    description = factory.Faker("paragraph", nb_sentences=5)
    category = factory.Iterator(Category.objects.all())
    # category = factory.SubFactory(CategoryFactory)
    posted_at = factory.Faker("date_time_this_year")
    is_public = factory.Faker("boolean", chance_of_getting_true=75)
    slug = factory.LazyAttribute(
        lambda obj: slugify(f"{obj.title} {obj.author.username} {obj.category.name}")
        + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
    )


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    author = factory.Iterator(CustomUser.objects.all())
    # author = factory.SubFactory(CustomUserFactory)  # Change this line
    blog = factory.Iterator(Blog.objects.all())
    # blog = factory.SubFactory(BlogFactory)  # Change this line
    text = factory.Faker("paragraph", nb_sentences=5)
    created_at = factory.Faker("date_time_this_year")


class ReplyFactory(DjangoModelFactory):
    class Meta:
        model = Reply

    # author = factory.SubFactory(CustomUserFactory)
    author = factory.Iterator(CustomUser.objects.all())
    # comment = factory.SubFactory(CommentFactory)
    comment = factory.Iterator(Comment.objects.all())
    text = factory.Faker("paragraph", nb_sentences=3)
    created_at = factory.Faker("date_time_this_year")


class LikeFactory(DjangoModelFactory):
    class Meta:
        model = Like

    author = factory.Iterator(CustomUser.objects.all())
    blog = factory.Iterator(Blog.objects.all())
    created_at = factory.Faker("date_time_this_year")


class ReactionFactory(DjangoModelFactory):
    class Meta:
        model = Reaction

    author = factory.Iterator(CustomUser.objects.all())
    blog = factory.Iterator(Blog.objects.all())
    comment = factory.Iterator(Comment.objects.all())
    reaction_type = factory.Iterator(
        [choice[0] for choice in Reaction.ReactionTypes.choices]
    )
    given_at = factory.Faker("date_time_this_year")


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"Tag {n}")
