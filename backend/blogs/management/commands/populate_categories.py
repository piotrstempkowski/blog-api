from django.core.management.base import BaseCommand

from blogs.factories import CategoryFactory, CATEGORY_NAMES


class Command(BaseCommand):
    help = "Populate the database with fake categories"

    def handle(self, *args, **options):
        # Clear existing Category instances
        CategoryFactory._meta.model.objects.all().delete()

        # Create new fake categories
        CategoryFactory.create_batch(len(CATEGORY_NAMES))

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully populated the database with fake categories"
            )
        )
