from __future__ import unicode_literals

from django.db import models
from django.conf import settings


class Post(models.Model): 
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts')
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=100)
    important = models.BooleanField(default=False)


class PostReply(models.Model):
    post = models.ForeignKey(Post, related_name='replies')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='replies')
    content = models.CharField(max_length=100)
