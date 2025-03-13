from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'avatar', 'avatar_url', 'role']
        extra_kwargs = {
            'avatar': {'write_only': True}
        }
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return None
        
    def update(self, instance, validated_data):
        avatar = validated_data.pop('avatar', None)
        if avatar:
            from .utils import resize_avatar
            instance.avatar = resize_avatar(avatar)
        return super().update(instance, validated_data)

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user
class ActivitySerializer(serializers.Serializer):
    type = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    object = serializers.SerializerMethodField()
    
    def get_object(self, obj):
        if obj['type'] == 'post':
            return PostSerializer(obj['object'], context=self.context).data
        elif obj['type'] == 'comment':
            return CommentSerializer(obj['object'], context=self.context).data
        return None