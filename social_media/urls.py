from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, PostViewSet

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet, basename="profile")
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "social_media"
