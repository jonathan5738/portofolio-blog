from rest_framework.response import Response 
from rest_framework import status 
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView 
from django.contrib.auth import authenticate
from . serializers import UserSerializer, LoginUserSerializer, ResetPasswordSerializer, ProfileSerializer
from . models import Profile

# Create your views here.

def user_formatted_data(user):
    token = Token.objects.get(user=user)
    response = {key: value for(key, value) in UserSerializer(user).data.items() if key != 'password'}
    response['token'] = token.key 
    return response

class RegisteUserView (APIView):
    parser_classes = [FormParser, MultiPartParser]
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        # print(request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = Profile.objects.create(avatar=request.data['avatar'], user=user)
            token = Token.objects.create(user=user)
            response = {key: value for(key, value) in UserSerializer(user).data.items() if key != 'password'}
            response['token'] = token.key
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            username, password = serializer.data.values()
            print(username, password)
            user = authenticate(username=username, password=password)
            if not user:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            response = user_formatted_data(user)
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditUserView(APIView):
    authentication_classes = [TokenAuthentication]
    def patch(self, request, *args, **kwargs):
        user = request.user 
        serializer = UserSerializer(user, data=request.data, partial=True) 
        if serializer.is_valid():
            user = serializer.save()
            response = user_formatted_data(user)
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = request.user 
        try:
            user.delete()
            return Response({'message': 'user successfully deleted'}, status=status.HTTP_200_OK)
        except:
            return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class ResetPasswordView(APIView):
    authentication_classes = [TokenAuthentication] 
    def patch(self, request, *args, **kwargs):
        user = request.user 
        serializer = ResetPasswordSerializer(data=request.data) 
        if serializer.is_valid():
            old_password, new_password, confirm_password = serializer.data.values()
            if not user.check_password(old_password):
                return Response({'error': 'unable to reset password'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not new_password == confirm_password:
                return Response({'error': 'both passwords must match'}, status=status.HTTP_404_NOT_FOUND)
            user.set_password(new_password)
            user.save()
            response = user_formatted_data(user)
            return Response (response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            