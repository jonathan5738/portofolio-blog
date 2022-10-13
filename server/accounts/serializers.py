from rest_framework import serializers 
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from . models import Profile


class ProfileSerializer(serializers.Serializer):
    avatar = serializers.ImageField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, inst, validated_data):
        inst.username = validated_data.get('username', inst.username)
        inst.first_name = validated_data.get('first_name', inst.first_name)
        inst.last_name = validated_data.get('last_name', inst.last_name)
        inst.email = validated_data.get('email', inst.email)
        inst.save()
        return inst


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200)

class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=100)
    new_password = serializers.CharField(max_length=100)
    confirm_password = serializers.CharField(max_length=100)

    def validate_old_password(self, old_pass):
        if validate_password(old_pass) == None:
            return old_pass 

    def validate_new_password(self, new_password):
        if validate_password(new_password) == None:
            return new_password 

    def validate_confirm_password(self, confirm_password):
        if validate_password(confirm_password) == None:
            return confirm_password 
