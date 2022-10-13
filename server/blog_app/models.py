from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return f'{self.name}'

class BlogGroup(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(blank=True)
    description = models.TextField()
    admin = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='blog_group')
    members = models.ManyToManyField(get_user_model(), blank=True, related_name='join_groups')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category', default=None)
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ('admin', 'admin level permission'),
            ('staff', 'staff member permission'),
            ('author', 'author permission'),
            ('premium_user', 'premium user permission')
        )
    
    def __str__(self):
        return f'{self.name}'

class Paragraph(models.Model):
    subtitle = models.CharField(max_length=200)
    image = models.ImageField(upload_to="paragraph_img", blank=True, null=True)
    content = models.TextField()
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='paragraphs')



class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    introduction = models.TextField()

    blog_group = models.ForeignKey(BlogGroup, on_delete=models.CASCADE, related_name='blog_posts')
    author = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, related_name='posts')
    published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    likes = models.JSONField(default=dict, blank=True)
    dislikes = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'{self.title}/{self.blog_group.name}'


class Comment(models.Model):
    username = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    content = models.TextField() 
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments') 

    likes = models.JSONField(default=dict, blank=True)
    dislikes = models.JSONField(default=dict, blank=True)
    added = models.DateTimeField(auto_now_add=True)


