from django.core.management.base import BaseCommand

from blogs.factories import (
    CustomUserFactory,
    CommentFactory,
    CategoryFactory,
    BlogFactory,
    ReplyFactory,
    LikeFactory,
    ReactionFactory,
    TagFactory,
)


class Command(BaseCommand):
    help = "Populate database with fake data using factory boy."

    def add_arguments(self, parser):
        parser.add_argument("num_users", type=int, help="Number of users to create")
        parser.add_argument(
            "num_categories", type=int, help="Number of categories to create"
        )
        parser.add_argument("num_blogs", type=int, help="Number of blogs to create")
        parser.add_argument(
            "num_comments", type=int, help="Number of comments to create"
        )
        parser.add_argument("num_likes", type=int, help="Number of likes to create")
        parser.add_argument("num_replies", type=int, help="Number of replies to create")
        parser.add_argument(
            "num_reactions", type=int, help="Number of reactions to create"
        )
        parser.add_argument("num_tags", type=int, help="Number of tags to create")

    def handle(self, *args, **options):
        num_users = options["num_users"]
        num_categories = options["num_categories"]
        num_blogs = options["num_blogs"]
        num_comments = options["num_comments"]
        num_replies = options["num_replies"]
        num_likes = options["num_likes"]
        num_reactions = options["num_reactions"]
        num_tags = options["num_tags"]

        # Create users
        for _ in range(num_users):
            CustomUserFactory.create()

        # Create categories
        for _ in range(num_categories):
            CategoryFactory.create()

        # Create blogs
        for _ in range(num_blogs):
            BlogFactory.create()

        # Create comments
        for _ in range(num_comments):
            CommentFactory.create()

        # Create replies
        for _ in range(num_replies):
            ReplyFactory.create()

        # Create likes
        for _ in range(num_likes):
            LikeFactory.create()

        # Create reactions
        for _ in range(num_reactions):
            ReactionFactory.create()

        # Create tags
        for _ in range(num_tags):
            TagFactory.create()

        self.stdout.write(
            self.style.SUCCESS("Successfully populated the database with fake data.")
        )
