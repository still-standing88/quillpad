from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField
from taggit.managers import TaggableManager
from markdownx.models import MarkdownxField

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='title', unique=True)
    #author = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = MarkdownxField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    featured_image = models.ImageField(upload_to='post_images/%Y/%m/', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)

    def increment_view(self):
        self.view_count += 1
        self.save(update_fields=['view_count']) 

    def __str__(self):
        return self.title

class Comment(models.Model):
    #post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    #author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    @property
    def is_reply(self):
        return self.parent is not None
    def __str__(self):
        return f'Comment by {self.author} on {self.post}'

class PostLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')

class SavedPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')