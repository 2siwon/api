from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'username',
            'img_profile',
            'age',
        )


class SignupSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'pk',
            'username',
            'password1',
            'password2',
            'age',
            'token',
        )

    # def get_token(self, obj):
    #     return Token.objects.create(user=obj).key
    @staticmethod
    def get_token(obj):
        return Token.objects.create(user=obj).key

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('비밀번호가 일치하지 않습니다')
        return data

    def create(self, validated_data):
        # User.objects.create_user와 같은 의미
        return self.Meta.model.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password1'],
            age=validated_data['age'],
        )
