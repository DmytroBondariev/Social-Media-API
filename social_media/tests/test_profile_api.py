from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from social_media.models import Profile, Post
from social_media.serializers import ProfileDetailSerializer

PROFILE_URL = reverse("social_media:profile-list")


def sample_profile(user, **params):
    defaults = {
        "username": "test_user2",
        "bio": "test bio",
        "status": "test status",
    }
    defaults.update(params)

    return Profile.objects.create(user=user, **defaults)


class UnauthenticatedPostApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedProfileApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_profile_detail(self):
        profile = sample_profile(user=self.user)
        profile.posts.add(
            Post.objects.create(
                title="Test post", content="Test content", author=profile
            )
        )

        res = self.client.get(reverse("social_media:profile-detail", args=[profile.id]))

        serializer = ProfileDetailSerializer(profile)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


def test_follow_unfollow(self):
    other_user = get_user_model().objects.create_user("other@test.com", "testpass")
    other_profile = sample_profile(other_user, username="other_user")

    res = self.client.post(
        reverse("social_media:profile-follow", args=[other_profile.id])
    )
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertTrue(
        self.profile.following.filter(username=other_profile.username).exists()
    )

    res = self.client.post(
        reverse("social_media:profile-unfollow", args=[other_profile.id])
    )
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertFalse(
        self.profile.following.filter(username=other_profile.username).exists()
    )
