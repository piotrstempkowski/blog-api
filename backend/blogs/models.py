import random
import string

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify

User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

    @property
    def blogs_amount(self):
        return self.blogs.count()


class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs")
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="blogs"
    )
    posted_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    slug = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(
                self.title + " " + self.author.username + " " + self.category.name
            )
            self.slug = base_slug + "".join(
                random.choice(string.ascii_letters + string.digits) for _ in range(5)
            )
        super().save(*args, **kwargs)


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="comments"
    )
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author} commented on {self.blog}."


class Reply(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="replies"
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="replies"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author} replied to {self.comment}"


class Like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} liked {self.blog}"


class Reaction(models.Model):
    class ReactionTypes(models.TextChoices):
        LIKE = "Like"
        LOVE = "Love"
        HAHA = "Haha"
        WOW = "WOW"
        SAD = "SAD"
        ANGRY = "Angry"

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    blog = models.ForeignKey(
        Blog, on_delete=models.SET_NULL, null=True, related_name="reactions"
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.SET_NULL, null=True, related_name="reactions"
    )
    reaction_type = models.CharField(max_length=10, choices=ReactionTypes.choices)
    given_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} reacted {self.reaction_type}"


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)
    blogs = models.ManyToManyField(Blog, related_name="tags")
    comments = models.ManyToManyField(Comment, related_name="tags")

    def __str__(self):
        return self.name
