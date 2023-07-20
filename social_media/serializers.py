from rest_framework import serializers

from social_media.models import Comment, Post, Profile


class CommentSerializer(serializers.ModelSerializer):
    read_only_fields = ("author", "post", "created_at")

    class Meta:
        read_only_fields = ("author", "post", "created_at")
        model = Comment
        fields = (
            "author",
            "post",
            "content",
            "created_at",
        )
        ordering = ("-created_at",)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "username",
            "status",
            "profile_pic",
            "bio",
        )


class ProfileListSerializer(ProfileSerializer):
    followers = serializers.IntegerField(source="followers.count")
    following = serializers.IntegerField(source="following.count")

    class Meta:
        model = Profile
        fields = (
            "username",
            "status",
            "profile_pic",
            "bio",
            "followers",
            "following",
        )


class ProfileDetailSerializer(ProfileSerializer):
    followers = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )
    following = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )

    class Meta:
        model = Profile
        fields = (
            "username",
            "status",
            "profile_pic",
            "bio",
            "followers",
            "following",
        )


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("profile_pic",)


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field="username")
    comments = serializers.IntegerField(source="comments.count", read_only=True)
    likes = serializers.IntegerField(source="likes.count", read_only=True)
    write_only_fields = ("scheduled_time",)

    class Meta:
        model = Post
        fields = (
            "author",
            "title",
            "content",
            "created_at",
            "image",
            "comments",
            "likes",
            "scheduled_time",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field="username")
    comments = CommentSerializer(many=True, read_only=True)
    likes = serializers.IntegerField(source="likes.count", read_only=True)
    write_only_fields = ("scheduled_time",)

    class Meta:
        model = Post
        fields = (
            "author",
            "title",
            "content",
            "created_at",
            "image",
            "comments",
            "likes",
            "scheduled_time",
        )


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("image",)
