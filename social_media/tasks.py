from datetime import datetime

from celery import shared_task
from django.utils import timezone
from .models import Post


@shared_task
def create_scheduled_post(title, content, author_id, scheduled_time, image=None):
    if scheduled_time:
        scheduled_time = timezone.make_aware(scheduled_time)
    else:
        scheduled_time = timezone.now()
    post = Post.objects.create(
        title=title, content=content, author_id=author_id, created_at=scheduled_time, image=image
    )
    return post.id
