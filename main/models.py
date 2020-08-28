from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return self.slug


class Like(models.Model):
    user = models.ForeignKey(get_user_model(), related_name='likes', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Post(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='posts')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts', blank=True)
    tags = models.ManyToManyField(Tag, related_name='tags', blank=True)
    likes = GenericRelation(Like)

    def __str__(self):
        return self.text

    @property
    def total_likes(self):
        return self.likes.count()


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='followings')
    follower = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        return f'user: {self.user}, followers: {self.follower}'
