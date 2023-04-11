from django.core.management.base import BaseCommand

from accounts.factories import CustomUserFactory


class Command(BaseCommand):
    help = "Populate the database with fake categories"

    def handle(self, *args, **options):
        # Clear existing User isntances
        CustomUserFactory._meta.model.objects.all().delete()

        # Create new fake users
        CustomUserFactory.create_batch(50)

        self.stdout.write(
            self.style.SUCCESS("Successfully populated the database with fake users.")
        )
