import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from social_media.models import Profile, Post, Comment
from social_media.serializers import (
    ProfileSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
)

POST_URL = reverse("social_media:post-list")


def sample_post(**params):
    defaults = {
        "title": "Sample post",
        "content": "Sample content",
    }
    defaults.update(params)

    return Post.objects.create(**defaults)


def sample_profile(user, **params):
    defaults = {
        "username": "test_user2",
        "bio": "test bio",
        "status": "test status",
    }
    defaults.update(params)

    return Profile.objects.create(user=user, **defaults)


def image_upload_url(post_id):
    """Return URL for recipe image upload"""
    return reverse("social_media:post-upload-image", args=[post_id])


class UnauthenticatedPostApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(POST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPostApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)
        self.profile = Profile.objects.create(
            user=self.user, username="test_user", bio="test bio", status="test status"
        )

    def test_list_posts(self):
        sample_post(author=self.profile)
        sample_post(author=self.profile)

        res = self.client.get(POST_URL)

        posts = Post.objects.order_by("id")
        serializer = PostListSerializer(posts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(res.data, serializer.data)

    def test_filter_posts_by_title(self):
        post1 = sample_post(author=self.profile, title="Post 1")
        post2 = sample_post(author=self.profile, title="Post 2")

        res = self.client.get(POST_URL, {"title": f"{post1.title}"})

        serializer1 = PostListSerializer(post1)
        serializer2 = PostListSerializer(post2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_posts_by_author(self):
        other_user = get_user_model().objects.create_user("other@test.com", "testpass")
        other_profile = sample_profile(other_user, username="other_user")

        post1 = sample_post(author=self.profile, title="Post 1")
        post2 = sample_post(author=other_profile, title="Post 2")

        res = self.client.get(POST_URL, {"author": f"{self.profile.username}"})

        serializer1 = PostListSerializer(post1)
        serializer2 = PostListSerializer(post2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_comment_on_post(self):
        post = sample_post(author=self.profile)
        payload = {
            "author": self.profile.id,
            "post": post.id,
            "content": "This is a test comment.",
        }

        res = self.client.post(
            reverse("social_media:post-comment", args=[post.id]), payload
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual("{'detail': 'Comment added successfully.'}", str(res.data))

    def test_like_and_unlike_post(self):
        post = sample_post(author=self.profile)
        res = self.client.post(reverse("social_media:post-like-unlike", args=[post.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.profile.posts_liked.filter(id=post.id).exists())

        res = self.client.post(reverse("social_media:post-like-unlike", args=[post.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(self.profile.posts_liked.filter(id=post.id).exists())


class PostImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)
        self.profile = sample_profile(user=self.user)
        self.post = sample_post(author=self.profile)

    def tearDown(self):
        self.post.image.delete()

    def test_upload_image_to_post(self):
        """Test uploading an image to a post"""
        url = image_upload_url(self.post.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.post.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.post.image.path))
