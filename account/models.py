from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, image, *args, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, image=image)
        user.set_password(password)
        user.create_activation_code()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, *args, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='', blank=True)
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=50, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def create_activation_code(self):
        import hashlib
        string_to_encode = self.email + str(self.id)
        encode_string = string_to_encode.encode()
        md5_object = hashlib.md5(encode_string)
        activation_code = md5_object.hexdigest()
        self.activation_code = activation_code

lass Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # img = models.ImageField()
    following = models.ManyToManyField(User, related_name="followers", blank=True)

    def follow(self, user):
        if self.following.filter(id=user.id).exists():  # If user already follows other, unfollow
            self.following.remove(user)
        else:
            self.following.add(user)

        self.save()

    def __str__(self):
        return self.user  # When outputting in console, show user


# Whenever user is created, give it a profile and a token
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)