from rest_framework import serializers
from .models import Post, Category, Comment
from taggit.serializers import (TagListSerializerField, TaggitSerializer)
from taggit.models import Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'post_count']
    
    def get_post_count(self, obj):
        return Post.objects.filter(tags__name__in=[obj.name]).count()

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class PostSerializer(TaggitSerializer, DynamicFieldsModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    tags = TagListSerializerField()
    category = serializers.SlugRelatedField(slug_field='name', queryset=Category.objects.all(), required=False, allow_null=True)
    comment_count = serializers.SerializerMethodField()
    featured_image_url = serializers.SerializerMethodField()
    id = serializers.IntegerField(read_only=True)

    
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'author', 'created_at', 
                 'updated_at', 'tags', 'category', 'comment_count', 
                 'featured_image', 'featured_image_url', 'is_published', 
                 'featured', 'view_count']
        extra_kwargs = {
            'featured_image': {'write_only': True}
        }
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            return self.context['request'].build_absolute_uri(obj.featured_image.url)
        return None    

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_serializer(self, *args, **kwargs):
        fields = self.request.query_params.get('fields', None)
        if fields:
            kwargs['fields'] = fields.split(',')
        return super().get_serializer(*args, **kwargs)

class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, instance):
        serializer = self.parent.parent.__class__(instance, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    author_avatar = serializers.SerializerMethodField()
    replies = RecursiveCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_avatar', 'content', 'created_at', 'parent', 'replies']
    
    def get_author_avatar(self, obj):
        if obj.author and obj.author.avatar:
            return self.context['request'].build_absolute_uri(obj.author.avatar.url)
        return None 

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