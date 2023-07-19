from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Profile, Post
from .serializers import (
    ProfileSerializer,
    ProfileDetailSerializer,
    ProfileImageSerializer,
    ProfileListSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().prefetch_related("followers", "following")

    def get_queryset(self):
        queryset = self.queryset
        username = self.request.query_params.get("username", None)

        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        elif self.action == "retrieve":
            return ProfileDetailSerializer
        elif self.action == "upload_image":
            return ProfileImageSerializer

        return ProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user.is_authenticated:
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"detail": "You must be logged in to create a profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        if instance.user == request.user:
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "You are not authorized to update this profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.user == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "You are not authorized to delete this profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        profile = self.get_object()
        user_profile = self.request.user.profile

        if user_profile != profile and profile not in user_profile.following.all():
            user_profile.follow(profile)
            return Response(
                {"detail": "Profile followed successfully."}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "Unable to follow the profile."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        profile = self.get_object()
        user_profile = self.request.user.profile

        if user_profile != profile and profile in user_profile.following.all():
            user_profile.unfollow(profile)
            return Response(
                {"detail": "Profile unfollowed successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "Unable to unfollow the profile."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAuthenticated],
    )
    def upload_image(self, request, pk=None):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)

        if profile.user == request.user:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "You are not authorized to update this profile."},
            status=status.HTTP_403_FORBIDDEN,
        )


class PostViewSet(viewsets.ModelViewSet):
    queryset = (
        Post.objects.all()
        .prefetch_related("comments")
        .select_related("author")
        .order_by("-created_at")
    )

    def get_queryset(self):
        user = self.request.user
        author = self.request.query_params.get("author", None)
        title = self.request.query_params.get("title", None)

        queryset = self.queryset.filter(
            author__in=user.profile.following.all() | Profile.objects.filter(user=user)
        )

        if author:
            queryset = queryset.filter(author__username__icontains=author)
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "comment":
            return CommentSerializer
        return PostListSerializer

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            scheduled_time = serializer.validated_data.get("scheduled_time")

            if scheduled_time:
                from .tasks import create_scheduled_post

                # Schedule the post using Celery
                create_scheduled_post.apply_async(
                    args=[
                        serializer.validated_data["title"],
                        serializer.validated_data["content"],
                        request.user.profile.id,
                        scheduled_time,
                    ],
                    eta=scheduled_time,  # The scheduled time to create the post
                )

                return Response(
                    {"detail": "Post scheduled for creation."},
                    status=status.HTTP_201_CREATED,
                )
            else:
                serializer.save(author=request.user.profile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"detail": "You must be logged in to create a post."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        if instance.author.user == request.user:
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "You are not authorized to update this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.author.user == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "You are not authorized to delete this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAuthenticated],
    )
    def upload_image(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if post.author.user == request.user:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "You are not authorized to update this post."},
            status=status.HTTP_403_FORBIDDEN,
        )

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        user_profile = self.request.user.profile
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                author=user_profile,
                post=post,
                content=serializer.validated_data["content"],
            )

            return Response(
                {"detail": "Comment added successfully."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=True, permission_classes=[IsAuthenticated])
    def like_unlike(self, request, pk=None):
        post = self.get_object()
        user_profile = self.request.user.profile

        if user_profile not in post.likes.all():
            post.likes.add(user_profile)
            return Response(
                {"detail": "Post liked successfully."}, status=status.HTTP_200_OK
            )

        post.likes.remove(user_profile)
        return Response(
            {"detail": "Your like was removed."},
            status=status.HTTP_200_OK,
        )

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def liked_posts(self, request):
        user_profile = self.request.user.profile
        queryset = Post.objects.filter(likes=user_profile)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
