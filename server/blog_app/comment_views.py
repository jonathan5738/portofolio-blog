from xml.etree.ElementTree import Comment
from rest_framework import status 
from rest_framework.views import APIView 
from rest_framework.authentication import TokenAuthentication 
from rest_framework.response import Response
from . models import BlogGroup, Post, Comment
from . serializer import CommentSerializer

class SubmitCommentView(APIView):
    authentication_classes = [TokenAuthentication]
    def post(self, request, *args, **kwargs):
        user = request.user 
        post_slug = kwargs['post_slug'] 
        blog_slug = kwargs['blog_group'] 
        try:
            post = user.join_groups.get(slug=blog_slug).blog_posts.get(slug=post_slug)
        except Post.DoesNotExist:
            return Response({'error': 'unable to find post'}, status=status.HTTP_404_NOT_FOUND) 
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(member=user, username=user.username, post=post)
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListCommentView(APIView):
    def get(self, request, *args, **kwargs):
        post_slug = kwargs['post_slug'] 
        blog_slug = kwargs['blog_group'] 
        ORDER_BY = None or 'likes'
        try:
            blog_group = BlogGroup.objects.get(slug=blog_slug)
            comments = blog_group.blog_posts.get(slug=post_slug).comments.all().order_by(ORDER_BY)
        except:
            return Response({'error': 'unable to find this resource'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LikeCommentView(APIView):
    authentication_classes = [TokenAuthentication]
    def post(self, request, *args, **kwargs):
        user = request.user 
        post_slug = kwargs['post_slug'] 
        blog_slug = kwargs['blog_group'] 
        comment_id = kwargs['comment_id']
        try:
            post = user.join_groups.get(slug=blog_slug).blog_posts.get(slug=post_slug)
        except Post.DoesNotExist:
            return Response({'error': 'unable to find post'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            comment = post.comments.get(pk=comment_id)
        except: 
            return Response({'error': 'comment not found'}, status=status.HTTP_404_NOT_FOUND)
        alreadyLiked = False
        if str(user.pk) in comment.dislikes.keys():
            comment.dislikes.pop(str(user.pk))

        if str(user.pk) in comment.likes.keys():
            alreadyLiked = True

        if not alreadyLiked:
            comment.likes[str(user.pk)] = {'userId': user.pk, 'like': 1}
        comment.save()
        return Response(CommentSerializer(Comment.objects.all(), many=True).data,
         status=status.HTTP_200_OK)

class DislikeCommentView(APIView):
    authentication_classes = [TokenAuthentication]
    def post(self, request, *args, **kwargs):
        user = request.user 
        post_slug = kwargs['post_slug'] 
        blog_slug = kwargs['blog_group'] 
        comment_id = kwargs['comment_id']
        try:
            post = user.join_groups.get(slug=blog_slug).blog_posts.get(slug=post_slug)
        except Post.DoesNotExist:
            return Response({'error': 'unable to find post'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            comment = post.comments.get(pk=comment_id)
        except: 
            return Response({'error': 'comment not found'}, status=status.HTTP_404_NOT_FOUND)
        print("********* comment received ***********")
        print(comment)
        alreadyDisliked = False 
        if str(user.pk) in comment.likes.keys():
            comment.likes.pop(str(user.pk))

        if str(user.pk) in comment.dislikes.keys():
            alreadyDisliked = True

        if not alreadyDisliked:
            comment.dislikes[str(user.pk)] = {'userId': user.pk, 'dislike': 1}
        comment.save()
        return Response(CommentSerializer(Comment.objects.all(), many=True).data,
         status=status.HTTP_200_OK)



