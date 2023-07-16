import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify


def profile_pic_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.email)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/profile_pics/", filename)


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    profile_pic = models.ImageField(
        upload_to=profile_pic_file_path, blank=True, null=True
    )
    bio = models.TextField(blank=True)
