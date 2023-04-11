from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass

    @property
    def blogs_amount(self):
        return self.blogs.count()

    @property
    def deleted(self):
        if self.is_staff == False:
            return True

    # @property
    # def category_count(self):
    #     return self.categories.count()
