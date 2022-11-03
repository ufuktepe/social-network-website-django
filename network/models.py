from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    User model that inherits from AbstractUser
    """
    pass


class Post(models.Model):
    """
    Post model that stores various attributes of a single post item
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(editable=True)
    posted_on = models.DateTimeField(auto_now_add=True)
    user_likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    class Meta:
        # Sort posts by posted_on when queried so that posts made recently will appear first. The minus sign
        # is used to sort the posts in descending order.
        ordering = ["-posted_on"]

    def __str__(self):
        return f"{self.author} - {self.posted_on.date()} - {self.posted_on.time()}"


class Profile(models.Model):
    """
    Profile model that stores the following list for each user
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    following = models.ManyToManyField(User, related_name="followers", blank=True)

    def __str__(self):
        return f"{self.user.username}"