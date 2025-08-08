
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from django.db import transaction
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import ( extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiResponse, OpenApiExample, OpenApiRequest
)
from .models import Post, SubPost
from .serializers import PostSerializer, SubPostSerializer



from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiResponse, OpenApiExample, OpenApiTypes
)

from .models import Post
from .serializers import PostSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Список постов",
        description="Возвращает список постов, отсортированный по `created_at` по убыванию.",
        tags=["Posts"],
        responses={200: PostSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary="Получить пост",
        description="Возвращает один пост по ID.",
        tags=["Posts"],
        responses={200: PostSerializer}
    ),
    destroy=extend_schema(
        summary="Удалить пост",
        tags=["Posts"]
    ),
    partial_update=extend_schema(
        summary="Частично обновить пост",
        tags=["Posts"]
    ),
    update=extend_schema(
        summary="Обновить пост",
        tags=["Posts"]
    ),
)
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
    summary="Создать пост(ы)",
    description=(
        "Создаёт один или несколько постов.\n\n"
        "- Можно отправить один объект или массив объектов."
    ),
    tags=["Posts"],
    request=PostSerializer(many=True),
    responses={
    201: PostSerializer(many=True),
    400: OpenApiResponse(description="Ошибка валидации"),
    }
  
)
    def create(self, request, *args, **kwargs):
        is_bulk = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_bulk)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = serializer.data
        if not is_bulk:
            data = [data]  # всегда массив
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        summary="Лайк/анлайк поста",
        description=(
            "Тогглит лайк текущего пользователя на посте.\n\n"
            "Возвращает текущее состояние и общее количество лайков."
        ),
        tags=["Posts"],
        request=None,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "liked": {"type": "boolean", "example": True},
                        "likes_count": {"type": "integer", "example": 5},
                    },
                    "required": ["liked", "likes_count"]
                },
                description="Состояние лайка и количество лайков"
            ),
            401: OpenApiResponse(description="Требуется аутентификация")
        },
        operation_id="posts_like_toggle",
    )
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

    @extend_schema(
        summary="Увеличить счётчик просмотров",
        description=(
            "Атомарно увеличивает поле `views` поста на 1 и возвращает новое значение."
        ),
        tags=["Posts"],
        request=None,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {"views": {"type": "integer", "example": 42}},
                    "required": ["views"]
                },
                description="Текущее количество просмотров"
            )
        },
        operation_id="posts_view_increment",
    )
    @action(detail=True, methods=['GET'])
    def view(self, request, pk=None):
        post = self.get_object()

        with transaction.atomic():
            Post.objects.filter(pk=post.pk).update(views=F('views') + 1)

        post.refresh_from_db()
        return Response({'views': post.views})



###subpostview



@extend_schema_view(
    list=extend_schema(
        summary="Список субпостов",
        description="Возвращает список субпостов, отсортированный по `created_at` по убыванию.",
        tags=["SubPosts"],
        responses={200: SubPostSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary="Получить субпост",
        description="Возвращает один субпост по ID.",
        tags=["SubPosts"],
        responses={200: SubPostSerializer}
    ),
    create=extend_schema(
        summary="Создать субпост",
        description="Создаёт один субпост. Поля, рассчитываемые на сервере, помечайте как `read_only` в сериализаторе.",
        tags=["SubPosts"],
        request=SubPostSerializer,
        responses={201: SubPostSerializer}
    ),
    update=extend_schema(
        summary="Обновить субпост",
        tags=["SubPosts"],
        request=SubPostSerializer,
        responses={200: SubPostSerializer}
    ),
    partial_update=extend_schema(
        summary="Частично обновить субпост",
        tags=["SubPosts"],
        request=SubPostSerializer,
        responses={200: SubPostSerializer}
    ),
    destroy=extend_schema(
        summary="Удалить субпост",
        tags=["SubPosts"]
    ),
)
class SubPostViewSet(viewsets.ModelViewSet):
    queryset = SubPost.objects.all().order_by('-created_at')
    serializer_class = SubPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()

    @extend_schema(
        summary="Лайк/анлайк субпоста",
        description="Тогглит лайк текущего пользователя на субпосте и возвращает состояние и общее число лайков.",
        tags=["SubPosts"],
        request=None,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "liked": {"type": "boolean", "example": True},
                        "likes_count": {"type": "integer", "example": 7},
                    },
                    "required": ["liked", "likes_count"]
                },
                description="Состояние лайка и количество лайков"
            ),
            401: OpenApiResponse(description="Требуется аутентификация"),
        },
        operation_id="subposts_like_toggle",
        examples=[
            OpenApiExample(
                "Ответ при постановке лайка",
                value={"liked": True, "likes_count": 8},
                response_only=True,
            ),
            OpenApiExample(
                "Ответ при снятии лайка",
                value={"liked": False, "likes_count": 7},
                response_only=True,
            ),
        ],
    )
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

    @extend_schema(
        summary="Увеличить счётчик просмотров субпоста",
        description="Атомарно увеличивает поле `views` на 1 и возвращает новое значение.",
        tags=["SubPosts"],
        request=None,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {"views": {"type": "integer", "example": 42}},
                    "required": ["views"]
                },
                description="Текущее число просмотров"
            )
        },
        operation_id="subposts_view_increment",
        examples=[
            OpenApiExample(
                "Ответ",
                value={"views": 43},
                response_only=True,
            ),
        ],
    )
    @action(detail=True, methods=['GET'])
    def view(self, request, pk=None):
        subpost = self.get_object()
        with transaction.atomic():
            SubPost.objects.filter(pk=subpost.pk).update(views=F('views') + 1)

        subpost.refresh_from_db()
        return Response({'views': subpost.views})