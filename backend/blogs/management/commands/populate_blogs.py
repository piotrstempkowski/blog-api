from django.core.management.base import BaseCommand

from blogs.factories import BlogFactory


class Command(BaseCommand):
    help = "Populate the database with fake blogs"

    def handle(self, *args, **options):
        # Clear existing Category instances
        BlogFactory._meta.model.objects.all().delete()

        # Create new fake categories
        BlogFactory.create_batch(100)

        self.stdout.write(
            self.style.SUCCESS("Successfully populated the database with fake blogs")
        )
