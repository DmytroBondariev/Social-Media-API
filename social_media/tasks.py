from celery import shared_task
from django.utils import timezone
from .models import Post


@shared_task
def create_scheduled_post(title, content, author, scheduled_time, image=None):
    scheduled_time = timezone.make_aware(scheduled_time)
    post = Post.objects.create(
        title=title,
        content=content,
        author=author,
        created_at=scheduled_time,
        image=image
    )
    return post.id
