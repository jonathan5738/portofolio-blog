from rest_framework import status 
from rest_framework.views import APIView 
from rest_framework.authentication import TokenAuthentication 
from rest_framework.response import Response
from . serializer import CategorySerializer, PostSerializer 
from . models import Category
from dotenv import dotenv_values
config = dotenv_values(".env")

class CreateCategoryView(APIView):
    authentication_classes = [TokenAuthentication] 
    def post(self, request, *args, **kwargs):
        user = request.user 
        if int(config.get('ADMIN_ID')) != user.pk:
            return Response({'error': 'unauthorized action'}, status=status.HTTP_403_FORBIDDEN) 
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save() 
            return Response(CategorySerializer(category).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListCategoryView(APIView):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)