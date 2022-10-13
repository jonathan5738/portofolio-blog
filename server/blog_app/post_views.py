from rest_framework import status 
from rest_framework.response import Response 
from rest_framework.views import APIView 
from rest_framework.parsers import FormParser, MultiPartParser
from guardian.shortcuts import assign_perm
from rest_framework.authentication import TokenAuthentication

from accounts.serializers import UserSerializer
from . serializer import PostSerializer, ParagraphSerializer, CreatePostSerializer
from . models import Post, BlogGroup 
from accounts.models import Profile
from accounts.serializers import ProfileSerializer
from django.utils.text import slugify 
from uuid import uuid4


class IsAuthorPermissionView(APIView):
    authentication_classes = [TokenAuthentication]
    def post(self, request, *args, **kwargs):
        user = request.user
        post_slug = request.data.get('post_slug')
        try:
            user.posts.get(slug=post_slug)
        except Post.DoesNotExist:
            return Response({'isAuthor': False})
        return Response({'isAuthor': True})


class IsMemberPermissionView(APIView):
    authentication_classes = [TokenAuthentication] 
    def post(self, request, *args, **kwargs):
        user = request.user 
        group_slug = request.data.get('group_slug')
        try:
            user.join_groups.get(slug=group_slug)
        except BlogGroup.DoesNotExist:
            return Response({'ismember': False})
        return Response({'ismember': True})
        

class CreatePostView(APIView):
    authentication_classes = [TokenAuthentication] 
    def post(self, request, *args, **kwargs):
        user = request.user 
        group = kwargs['blog_group']
        try:
            blog_group = BlogGroup.objects.get(slug=group)
        except BlogGroup.DoesNotExist:
            return Response({'error': 'blog group not found'}, status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('author', blog_group):
            return Response({'error': 'unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = CreatePostSerializer(data=request.data) 
    
        if serializer.is_valid():
            post = serializer.save(blog_group=blog_group, author=user)
            slug = slugify(post.title + '-' + (str(uuid4())[0:8]) )
            post.slug = slug 
            post.save()
            return Response(PostSerializer(post).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LikePostView(APIView):
    authentication_classes = [TokenAuthentication] 
    def post(self, request, *args, **kwagrs):
        user = request.user 
        post_slug = kwagrs['post_slug']; blog_slug = kwagrs['blog_group']
        try:
            post = user.join_groups.get(slug=blog_slug).blog_posts.get(slug=post_slug)
        except:
            pass
        alreadyLiked = False
        if str(user.pk) in post.dislikes.keys():
            post.dislikes.pop(str(user.pk))

        if str(user.pk) in post.likes.keys():
            alreadyLiked = True

        if not alreadyLiked:
            post.likes[str(user.pk)] = {'userId': user.pk, 'like': 1}

        post.save()
        profile = Profile.objects.get(user=post.author)
        author = UserSerializer(profile.user)
        author = {key: value for (key, value) in author.data.items() if key != 'password'}
        author['avatar'] = profile.avatar.url
        serializer = PostSerializer(post)
        return Response([serializer.data, author], status=status.HTTP_200_OK)


class DisLikePostView(APIView):  
    authentication_classes = [TokenAuthentication] 
    def post(self, request, *args, **kwargs):
        print('*****dislike request received*****')
        user = request.user 
        post_slug = kwargs['post_slug']; blog_slug = kwargs['blog_group']
        try:
            post = user.join_groups.get(slug=blog_slug).blog_posts.get(slug=post_slug)
        except:
            pass
        alreadyDisliked = False 
        if str(user.pk) in post.likes.keys():
            post.likes.pop(str(user.pk))

        if str(user.pk) in post.dislikes.keys():
            alreadyDisliked = True

        if not alreadyDisliked:
            post.dislikes[str(user.pk)] = {'userId': user.pk, 'dislike': 1}
        post.save()
        profile = Profile.objects.get(user=post.author)
        author = UserSerializer(profile.user)
        author = {key: value for (key, value) in author.data.items() if key != 'password'}
        author['avatar'] = profile.avatar.url
        serializer = PostSerializer(post)
        return Response([serializer.data, author], status=status.HTTP_200_OK)




class PostPublicListView(APIView):
    def get(self, request, *args, **kwargs):
        blog_group= kwargs['blog_group']
        ORDER_BY = None or 'likes'
        try:
            group = BlogGroup.objects.get(slug=blog_group)
        except BlogGroup.DoesNotExist:
            return Response({'error': 'blog group not found'}, status=status.HTTP_404_NOT_FOUND)
        posts = group.blog_posts.all().order_by(ORDER_BY)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostDetailPublicView(APIView):
    def get(self, request, *args, **kwargs):
        post_slug = kwargs['post_slug']
        try:
            post = Post.objects.get(slug=post_slug)
        except Post.DoesNotExist:
            return Response({'error': 'post not found'}, status=status.HTTP_404_NOT_FOUND)
        profile = Profile.objects.get(user=post.author)
        author = UserSerializer(profile.user)
        author = {key: value for (key, value) in author.data.items() if key != 'password'}
        author['avatar'] = profile.avatar.url
        serializer = PostSerializer(post)
        return Response([serializer.data, author], status=status.HTTP_200_OK)
        

class PostPrivateListView(APIView):
    authentication_classes = [TokenAuthentication]
    def get(self, request, *args, **kwargs):
        user = request.user 
        try:
            posts = user.posts.all()
        except:
            return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostPrivateDetailView(APIView):
    authentication_classes = [TokenAuthentication] 
    def get(self, request, *args, **kwargs):
        user = request.user
        post_slug = kwargs['post_slug']
        try:
            post = user.posts.get(slug=post_slug)
        except Post.DoesNotExist:
            return Response({'error': 'post not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PostSerializer(post).data, status=status.HTTP_200_OK)

class AddParagraphView(APIView):
    authentication_classes = [TokenAuthentication] 
    parser_classes = [FormParser, MultiPartParser]
    def post(self, request, *args, **kwargs):
        user = request.user 
        blog_group = kwargs['blog_group']
        post_slug = kwargs['post_slug']
        try:
            post = user.posts.get(slug=post_slug)
        except Post.DoesNotExist:
            return Response({'error': 'post not found'}, status=status.HTTP_200_OK)
        
        serializer = ParagraphSerializer(data=request.data)
        if serializer.is_valid():
            paragraph = serializer.save(post=post)
            return Response(ParagraphSerializer(paragraph).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditParagraphView(APIView):
    authentication_classes = [TokenAuthentication] 
    def patch(self, request, *args, **kwargs):
        user = request.user
        post_slug = kwargs['post_slug'] 
        para_id = kwargs['para_id']
        try:
            post = user.posts.get(slug=post_slug)
        except Post.DoesNotExist:
            pass 
        paragraph = post.paragraphs.get(pk=para_id)
        serializer = ParagraphSerializer(paragraph, data=request.data, partial=True)
        if serializer.is_valid():
            paragraph = serializer.save()
            return Response(PostSerializer(post).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

    