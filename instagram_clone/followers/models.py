from django.db import models
from users.models import CustomUser


class Follower(models.Model):
    user_from = models.ForeignKey(
        CustomUser, related_name='following', on_delete=models.CASCADE)
    user_to = models.ForeignKey(
        CustomUser, related_name='followers', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user_from', 'user_to'),)
        ordering = ['-created']
        
    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"
