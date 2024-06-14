from django.db import models

from django.db import models
from django.conf import settings
from django.utils import timezone

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='post_images/')
    created_at = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL,  related_name='liked_posts', blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.caption}'
    
    @property
    def total_likes(self):
        return self.likes.count()

    def is_liked_by_user(self, user):
        return self.likes.filter(id=user.id).exists()

    def liked_users(self):
        return self.likes.all()


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    text = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} commented on {self.post}'

    @property
    def is_reply(self):
        return self.parent is not None

