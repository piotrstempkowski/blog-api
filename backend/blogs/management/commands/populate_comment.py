from django.core.management.base import BaseCommand

from blogs.factories import CommentFactory


class Command(BaseCommand):
    help = "Populate the database with fake categories"

    def handle(self, *args, **options):
        # Clear existing Category instances
        CommentFactory._meta.model.objects.all().delete()

        # Create new fake categories
        CommentFactory.create_batch(100)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully populated the database with fake comments."
            )
        )
