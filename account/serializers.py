from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from account.utils import send_activation_email

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirmation = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirmation', 'image')

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('User with given email already exist')
        return email

    def validate(self, validated_data):
        password = validated_data.get('password')
        password_confirmation = validated_data.get('password_confirmation')
        if password != password_confirmation:
            raise serializers.ValidationError('Passwords don\'t match')
        return validated_data

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        image = validated_data.get('image')
        user = User.objects.create_user(email, password, image)
        send_activation_email(user.email, user.activation_code)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'image', 'id')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.followers.all().count() > 0:
            followings_object_list = instance.followers.filter(follower=instance)
            followings_list = [follow.user.email for follow in followings_object_list]
            representation['followings'] = followings_list
        if instance.followings.all().count() > 0:
            followers_object_list = instance.followings.filter(user=instance)
            followers_list = [follow.follower.email for follow in followers_object_list]
            representation['followers'] = followers_list
        return representation


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email',)


