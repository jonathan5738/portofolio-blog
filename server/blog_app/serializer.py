from rest_framework import serializers 
from . models import Category, Post, Paragraph, Comment, BlogGroup
from django.utils.text import slugify 
from uuid import uuid4

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name'] 

class BlogGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    slug = serializers.SlugField(read_only=True)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000)

    def update(self, inst, validated_data):
        if 'name' in validated_data:
            slug = slugify(validated_data.get('name') + '-' + (str(uuid4())[0: 8]) )
            inst.slug = slug 
        inst.name = validated_data.get('name', inst.name)
        inst.description = validated_data.get('description', inst.description)
        inst.save()
        return inst

class ParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paragraph 
        fields = ['id', 'subtitle', 'content', 'image']

class PostSerializer(serializers.ModelSerializer):
    paragraphs = ParagraphSerializer(many=True)
    class Meta:
        model = Post 
        fields = ['id', 'title', 'introduction', 'slug', 'paragraphs', 'likes', 'dislikes'] 
    
    def create(self, validated_data):
        author = validated_data.pop('author')
        blog_group = validated_data.pop('blog_group')
        post = Post(author=author, blog_group=blog_group, **validated_data)
        post.save()
        return post


class CreatePostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    introduction = serializers.CharField(max_length=2000)
    def create(self, validated_data):
        blog_group = validated_data.pop('blog_group')
        author = validated_data.pop('author')
        post = Post(**validated_data, author=author, blog_group=blog_group)
        post.save()
        print('post:', post)
        return post


class ParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paragraph 
        fields = ['id', 'subtitle', 'image', 'content']

    def create(self, validated_data):
        post = validated_data.pop('post')
        paragraph = Paragraph(**validated_data)
        paragraph.post = post 
        paragraph.save()
        return paragraph



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment 
        fields = ['id', 'title', 'content', 'username', 'likes', 'dislikes'] 
        read_only_fields = ['username', 'likes', 'dislikes']
    
    def create(self, validated_data):
        member = validated_data.pop('member') 
        username = validated_data.pop('username')
        post = validated_data.pop('post')
        comment = Comment(user=member, post=post, username=username, **validated_data)
        comment.save()
        return comment


class ReplySerializer(serializers.Serializer):
    content = serializers.CharField(max_length=200)
    def create(self, validated_data):
        comment = validated_data.pop('comment') 
        submitted_by = validated_data.pop('submitted_by')
        reply = Reply(comment=comment, submitted_by=submitted_by, **validated_data)
        reply.save()
        return reply

