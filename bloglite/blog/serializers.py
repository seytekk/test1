from rest_framework import serializers
from .models import Post, SubPost
from users.serializers import RegisterSerializer as UserSerializer
from django.db import transaction
from drf_spectacular.utils import extend_schema_field, OpenApiTypes


        
class SubPostSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model=SubPost
        fields=['id','title','body','post','created_at','updated_at','views','likes_count'] 
        read_only_fields = ['post']
    @extend_schema_field(OpenApiTypes.INT)    
    def get_likes_count(self, obj):
        return obj.likes.count()
        
class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField(read_only=True)
    author = UserSerializer(read_only=True)  
    subposts = SubPostSerializer(many=True)
    class Meta:
        model=Post
        fields=['id','title','body','author','created_at','updated_at','views','subposts','likes_count']    
    @extend_schema_field(OpenApiTypes.INT)
    def get_likes_count(self, obj)-> int:
        return obj.likes.count()
    def create(self, validated_data):
        subposts_data=validated_data.pop('subposts')
        post=Post.objects.create(**validated_data)
        for sub_data in subposts_data:
            SubPost.objects.create(post=post,**sub_data)
        return post
    @transaction.atomic
    def update(self, instance, validated_data):
        subposts_data=validated_data.pop('subposts')
        instance.title=validated_data.get('title',instance.title)
        instance.save()
        
        existing_ids = [sub.id for sub in instance.subposts.all()]
        received_ids = [sub.get('id') for sub in subposts_data if sub.get('id')]
        for sub in instance.subposts.all():
            if sub.id not in received_ids:
                sub.delete()
        for sub_data in subposts_data:
            sub_id = sub_data.get('id')
            if sub_id:
                sub = SubPost.objects.get(id=sub_id, post=instance)
                sub.body = sub_data['body']
                sub.save()
            else:
                SubPost.objects.create(post=instance, **sub_data)
