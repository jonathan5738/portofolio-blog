from rest_framework import status 
from rest_framework.response import Response 
from rest_framework.views import APIView 
from rest_framework.authentication import TokenAuthentication 
from django.utils.text import slugify 
from uuid import uuid4
from guardian.shortcuts import assign_perm
from . models import BlogGroup, Category
from . serializer import BlogGroupSerializer 
from accounts.serializers import UserSerializer

class CreateBlogGroup(APIView):
    authentication_classes = [TokenAuthentication] 
    def post(self, request, *args, **kwargs):
        user = request.user 
        category_name = request.data.get('ct_name')
        serializer = BlogGroupSerializer(data=request.data)
        if serializer.is_valid():
            name, description = serializer.data.values()
            try:
                category = Category.objects.get(name=category_name)
            except:
                return Response({'error': 'unable to find category'}, status=status.HTTP_404_NOT_FOUND)
            try:
                blog_group = BlogGroup.objects.create(name=name, description=description, admin=user, category=category)
                slug = slugify(blog_group.name + '-' + (str(uuid4())[0:8]) )
                blog_group.slug = slug; blog_group.save()
                assign_perm('admin', user, blog_group)
            except:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
            return Response(BlogGroupSerializer(blog_group).data, status=status.HTTP_200_OK)

class BlogGroupDetail(APIView):
    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        try:
            blog_group = BlogGroup.objects.get(slug=slug)
        except BlogGroup.DoesNotExist:
            return Response({'error': 'blog group not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(BlogGroupSerializer(blog_group).data, status=status.HTTP_200_OK)
        
class ListBlogGroupView(APIView):
    def get(self, request, *args, **kwargs):
        category_name = kwargs.get('ct_name').lower()
        blog_groups = BlogGroup.objects.filter(category__name=category_name)
        serializer = BlogGroupSerializer(blog_groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PrivateListBlogGroupView(APIView):
    authentication_classes = [TokenAuthentication] 
    def get(self, request, *args, **kwargs):
        user = request.user 
        try:
            blogs = user.blog_group.all()
        except:
            return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = BlogGroupSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ListGroupMembers(APIView):
    authentication_classes = [TokenAuthentication] 
    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']; user = request.user
        try:
            group = user.blog_group.get(slug=slug)
            members = group.members.all()
        except:
            return Response({'error': 'something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        users = UserSerializer(members, many=True)
        list_members = []
        for user in users.data:
            data = {}; user = dict(user)
            if members.get(pk=user['id']).has_perm('author', group):
                data['permissions'] = 'author'
            elif members.get(pk=user['id']).has_perm('staff', group):
                data['permissions'] = 'staff'
            elif members.get(pk=user['id']).has_perm('staff', group) and members.get(pk=user['id']).has_perm('author', group):
                data['permissions'] = ['autor', 'staff']
            
            for (key, value) in user.items():
                if key == 'password': continue
                data[key] = value 
            list_members.append(data)
        return Response(list_members, status=status.HTTP_200_OK)


class JoinGroupView(APIView):
    authentication_classes = [TokenAuthentication]
    def post(self, request, *args, **kwargs):
        user = request.user
        slug = kwargs.get('slug')
        try:
            blog_group = BlogGroup.objects.get(slug=slug)
        except BlogGroup.DoesNotExist:
            return Response({'error': 'blog group not found'}, status=status.HTTP_404_NOT_FOUND) 
        blog_group.members.add(user)
        blog_group.save()
        return Response({}, status=status.HTTP_200_OK)

        
class AssignPermissionView(APIView):
    authentication_classes = [TokenAuthentication] 
    def get(self, request, *args, **kwargs):
        user = request.user 
        slug = kwargs['slug']
        member_username = request.query_params.get('username')
        try:
            group = user.blog_group.get(slug=slug)
        except BlogGroup.DoesNotExist:
            return Response({'error': 'blog group not found'}, status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('admin', group):
            return Response({'error': 'unauthorized access'}, status=status.HTTP_403_FORBIDDEN)
        member = group.members.get(username=member_username)
        response = {'id': member.id, 'username': member.username}
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user 
        slug = kwargs['slug']
        permission, member_id = request.data.values()
        try:
            group = user.blog_group.get(slug=slug)
        except BlogGroup.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        member = group.members.get(pk=int(member_id))
        assign_perm(permission, member, group)
        return Response({}, status=status.HTTP_200_OK)

        
        
class ManageBlogGroupView(APIView):
    authentication_classes = [TokenAuthentication] 
    def patch(self, request, *args, **kwargs):
        user = request.user; slug = kwargs['slug']
        try:
            blog_group = user.blog_group.get(slug=slug)
        except BlogGroup.DoesNotExist:
            return Response({'error': 'blog not found'}, status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('admin', blog_group):
            return Response({'error': 'action not allowed'}, status=status.HTTP_403_FORBIDDEN)
        serializer = BlogGroupSerializer(blog_group, data=request.data, partial=True)
        if serializer.is_valid():
            blog_group = serializer.save()
            return Response(BlogGroupSerializer(blog_group).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        user = request.user; slug = kwargs['slug']
        try:
            blog_group = user.blog_group.get(slug=slug)
        except BlogGroup.DoesNotExist:
            return Response({'error': 'blog not found'}, status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('admin', blog_group):
            return Response({'error': 'action not allowed'}, status=status.HTTP_403_FORBIDDEN)
        blog_group.delete()
        return Response({}, status=status.HTTP_200_OK)



class JoinedGroupListView(APIView):
    authentication_classes = [TokenAuthentication] 
    def get(self, request, *args, **kwagrs):
        '''we fetch groups joined by the current user and then check to see
           if the user has any permission in one of those joined groups
           if the user has a permission we modify the return data by adding a key
           which is the user permission(permission: true), so on the frontend we will unable user to certain actions
           based upon they permissions
        '''
        user = request.user 
        groups = user.join_groups.all()
        list_groups_perm = {}
        serializer = BlogGroupSerializer(groups, many=True)
        for group in groups:
            if user.has_perm('author', group):
                list_groups_perm[str(group.pk)] = {'permission': 'author'}
            if user.has_perm('staff', group):
                list_groups_perm[str(group.pk)] = {'permission': 'staff'}
            if user.has_perm('premium_user', group):
                list_groups_perm[str(group.pk)] = {'permission': 'premium_user'}

        if len(list(list_groups_perm.keys())) > 0:
            groups_id = [int(id) for id in list_groups_perm.keys()] # list id of groups where the user has permission
            for serializedGroup in serializer.data:
                if serializedGroup['id'] in groups_id:
                    permission = list_groups_perm[str(serializedGroup['id'])]['permission']
                    serializedGroup['permission'] = permission

        return Response(serializer.data, status=status.HTTP_200_OK)


class PrivateGroupDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    def get(self, request, *args, **kwargs):
        user = request.user 
        slug = kwargs['slug']
        try:
            group = user.join_groups.get(slug=slug)
        except BlogGroup.DoesNotExist:
            return Response({'error': 'group not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BlogGroupSerializer(group)
        response = serializer.data 
        if user.has_perm('author', group):
            response['author'] = True 
        if user.has_perm('staff', group): response['staff'] = True
        return Response(response, status=status.HTTP_200_OK)


class AuthorPermissionView(APIView):
    authentication_classes = [TokenAuthentication]
    def post(self, request, *args, **kwargs):
        user = request.user 
        group_slug = request.data.get('group_slug')
        try:
            group = user.join_groups.get(slug=group_slug)
        except BlogGroup.DoesNotExist:
            return Response({'error': 'group not found'}, status=status.HTTP_404_NOT_FOUND)
        if not user.has_perm('author', group):
            return Response({'author': False})
        return Response({'author': True}, status=status.HTTP_200_OK)