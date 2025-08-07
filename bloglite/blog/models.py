from django.db import models
from django.conf import settings 

# Create your models here.

class Post(models.Model):
    id = models.AutoField(primary_key=True)  
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)

    
    def __str__(self):
        return self.title
    
class SubPost(models.Model):
    id = models.AutoField(primary_key=True)  
    title = models.CharField(max_length=200)
    body = models.TextField()
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name="subposts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_subposts', blank=True)

    
    def __str__(self):
        return self.title
       