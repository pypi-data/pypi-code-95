from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create(self, username, email, password, * args, **kwargs):
        new_user = super().create(username=username, email=email, *args, **kwargs)
        new_user.set_password(password)
        new_user.save(using=self._db)
        return new_user

    def create_superuser(self, username, email, password):
        user = self.create(
            username=username, email=email, password=password)
        user.is_superuser = True
        user.save(using=self._db)
        return user
