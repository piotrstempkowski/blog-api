from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass

    @property
    def blogs_amount(self):
        return self.blogs.count()

    @property
    def deletable(self):
        return not self.is_staff

    # @property
    # def category_count(self):
    #     return self.categories.count()
