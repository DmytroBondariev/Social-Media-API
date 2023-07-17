import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify


def profile_pic_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.username)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/profile_pics/", filename)


class Profile(models.Model):
    username = models.CharField(max_length=50, unique=True)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    status = models.CharField(max_length=50, blank=True)
    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )
    profile_pic = models.ImageField(
        upload_to=profile_pic_file_path, blank=True, null=True
    )
    bio = models.TextField(blank=True)

    def follow(self, profile):
        self.following.add(profile)

    def unfollow(self, profile):
        self.following.remove(profile)

    @property
    def get_followers(self):
        return self.followers.all()

    @property
    def get_following(self):
        return self.following.all()


class Post(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    author = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
