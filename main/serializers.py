from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Post, Comment, Tag, Follow
from main import services as likes_services

User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user',)

    def create(self, validate_data):
        user_follow = validate_data.get('user')
        user_following = self.context['request'].user

        if Follow.objects.filter(user=user_follow, follower=user_following).exists():
            message = 'Have already following'
            raise serializers.ValidationError(message)
        elif user_following.id == user_follow.id:
            message = 'You cannot following yourself'
            raise serializers.ValidationError(message)
        else:
            follow = Follow.objects.create(
                user=user_follow,
                follower=user_following
            )
            return follow


class FanSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'full_name',
        )

    def get_full_name(self, obj):
        return obj.get_full_name()


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('text', 'post_id', 'created_at', 'id', 'author')

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author_id'] = request.user.id
        comment = Comment.objects.create(**validated_data)
        return comment

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = instance.author.email
        representation['text'] = instance.text
        return representation


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('title', 'slug')


class PostSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y %H:%M:%S', read_only=True)
    tags = serializers.SlugRelatedField(many=True, queryset=Tag.objects.all(), slug_field='slug')
    is_fan = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('text', 'image', 'created_at', 'id', 'tags', 'total_likes', 'is_fan')

    def get_is_fan(self, obj) -> bool:
        """Проверяет, лайкнул ли `request.user` твит (`obj`).
        """
        user = self.context.get('request').user
        return likes_services.is_fan(obj, user)

    def __get_image_url(self, instance):
        request = self.context.get('request')
        if instance.image:
            url = instance.image.url
            if request is not None:
                url = request.build_absolute_uri(url)
        else:
            url = ''
        return url

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author_id'] = request.user.id
        tags = validated_data.pop('tags')
        post = Post.objects.create(**validated_data)
        for tag in tags:
            post.tags.add(tag)
        return post

    def to_representation(self, instance):
        if 'comments' not in self.fields:
            self.fields['comments'] = CommentSerializer(instance, many=True)
        representation = super().to_representation(instance)
        representation['text'] = instance.text
        representation['author'] = instance.author.email
        representation['image'] = self.__get_image_url(instance)
        return representation
