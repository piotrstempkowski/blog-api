import factory
from factory.django import DjangoModelFactory

from .models import CustomUser


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "password123")

    # You can set other fields from the AbstractUser model here if needed, e.g.:
    # first_name = ...
    # last_name = ...
