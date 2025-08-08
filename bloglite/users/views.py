from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample
from .serializers import RegisterSerializer

class RegisterView(APIView):
    permission_classes = []

    @extend_schema(
        tags=["Auth"],
        summary="Регистрация",
        description="Создаёт пользователя и возвращает access/refresh токены.",
        request=RegisterSerializer,
        responses={
            201: inline_serializer(
                name="AuthResponse",
                fields={
                    "id": serializers.IntegerField(),
                    "username": serializers.CharField(),
                    "access": serializers.CharField(),
                    "refresh": serializers.CharField(),
                },
            ),
            400: None,
        },
        examples=[
            OpenApiExample(
                "Успешная регистрация",
                value={"id": 1, "username": "alice", "access": "xxx", "refresh": "yyy"},
                response_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        summary="Текущий пользователь",
        responses=inline_serializer(
            name="MeResponse",
            fields={
                "id": serializers.IntegerField(),
                "username": serializers.CharField(),
                "is_superuser": serializers.BooleanField(),
            },
        ),
    )
    def get(self, request):
        user = request.user
        return Response(
            {"id": user.id, "username": user.username, "is_superuser": user.is_superuser}
        )
