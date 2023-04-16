from django.dispatch import receiver
from django.db.models.signals import post_save,m2m_changed
from django.contrib.contenttypes.models import ContentType
from Blog.models import *

@receiver(post_save,sender=Comment)
def new_comment(instance,created,*args,**kwargs):
    if instance.commenter:
        commenter = instance.commenter.username
    else:
        commenter = "Anonymous"
    if created and instance.commenter != instance.post.author:
        notification = Notification(content_type=ContentType.objects.get_for_model(Comment),content_id=instance.id,user=instance.post.author)
        notification.content = f"{commenter} commented on your post {instance.post.title}."
        notification.type = 'Comment'
        notification.save()
    else:
        pass

@receiver(m2m_changed,sender=Post)
def post_status(instance,created,*args,**kwargs):
    pass