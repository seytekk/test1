# blog/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from django.db import transaction
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from .models import Post, SubPost
from .serializers import PostSerializer, SubPostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            return Response({'liked': False, 'likes_count': post.likes.count()})
        else:
            post.likes.add(user)
            return Response({'liked': True, 'likes_count': post.likes.count()})


    @action(detail=True, methods=['GET'])
    def view(self, request, pk=None):
        post = self.get_object()

        with transaction.atomic():
            Post.objects.filter(pk=post.pk).update(views=F('views') + 1)

        post.refresh_from_db()
        return Response({'views': post.views})


###subpostview



class SubPostViewSet(viewsets.ModelViewSet):
    queryset = SubPost.objects.all().order_by('-created_at')
    serializer_class = SubPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None):
        subpost = self.get_object()
        user = request.user

        if user in subpost.likes.all():
            subpost.likes.remove(user)
            return Response({'liked': False, 'likes_count': subpost.likes.count()})
        else:
            subpost.likes.add(user)
            return Response({'liked': True, 'likes_count': subpost.likes.count()})

    @action(detail=True, methods=['GET'])
    def view(self, request, pk=None):
        subpost = self.get_object()
        with transaction.atomic():
            SubPost.objects.filter(pk=subpost.pk).update(views=F('views') + 1)

        subpost.refresh_from_db()
        return Response({'views': subpost.views})
