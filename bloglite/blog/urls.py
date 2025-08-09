from rest_framework.routers import DefaultRouter
from .views import PostViewSet, SubPostViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'subposts', SubPostViewSet, basename='subpost')

urlpatterns = router.urls


