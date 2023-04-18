from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save
from django.contrib.contenttypes.models import ContentType
from Blog.models import *

#Additional function
def create_notification(model,instance,user,content,type):
    notification = Notification(content_type=ContentType.objects.get_for_model(model),content_id=instance.id,user=user)
    notification.content = content
    notification.type = type
    notification.save()

@receiver(post_save,sender=Comment)
def new_comment(instance,created,*args,**kwargs):
    if instance.commenter:
        commenter = instance.commenter.username
    else:
        commenter = "Anonymous"
    if created and instance.commenter != instance.post.author:
        content = f"{commenter} commented on your post {instance.post.title}.\n{instance.content[:20]}"
        create_notification(Comment,instance,instance.post.author,content,'Comment')
    else:
        pass

@receiver(pre_save,sender=Post)
def post_status(instance,*args,**kwargs):
    if instance.pk:
        post = Post.objects.get(pk=instance.pk)
        if post.status in ['Draft','Rejected','Pending'] and instance.status in 'Published':
            content = f"Your post {instance.title} has been Published."
            create_notification(Post,instance,instance.author,content,'Update')
        elif post.status != 'Hot' and instance.status == 'Hot':
            content = f"Your post {instance.title} has been choosen as hot post."
            create_notification(Post,instance,instance.author,content,'Update')
        elif post.status != 'Pending' and instance.status == 'Pending':
            content = f"Your post {instance.title} is now under review."
            create_notification(Post,instance,instance.author,content,'Update')
        elif post.status == 'Pending' and instance.status == 'Rejected':
            content = f"Your post {instance.title} has been rejected.\n Reason: {instance.note}"
            create_notification(Post,instance,instance.author,content,'Notice')

    else:
        pass

@receiver(pre_save,sender=AuthorUser)
def user_status(sender,instance,*args,**kwargs):
    role = ["Banned",'Contributor',"Author","Moderator","Admin"]
    if instance.pk:
        user = sender.objects.get(pk=instance.pk)
        if user.rank != 'Banned' and instance.rank == 'Banned':
            content = f"Dear {instance.username}, You are now banned, \n Reason {instance.note}."     
        elif role.index(user.rank) < role.index(instance.rank):
            content = f"Dear {instance.username}, Your rank updated from {user.rank} to {instance.rank}."
        elif role.index(user.rank) > role.index(instance.rank):
            content = f"Dear {instance.username}, Your rank downgraded from {user.rank} to {instance.rank}."
        else:
            pass
        try:
            create_notification(sender,instance,instance,content,'Notice')
        except:
            pass
    else:
        pass


@receiver(pre_save,sender=ReportContent)
def report_status_reviewed(sender,instance,*args,**kwargs):
    if instance.pk:
        reported_object = instance.report_to.__class__.__name__
        report = sender.objects.get(pk=instance.pk)
        if report.status != 'Solved' and instance.status == 'Solved':
            if reported_object == 'Post':
                content = f"Your report to the post {report.report_to.title} has been solved."
            elif reported_object == 'Comment':
                content = f"Your report to the comment of {report.report_to.commenter.username} has been solved."
        if report.status != 'Rejected' and instance.status == 'Rejected':
            if reported_object == 'Post':
                content = f"Your report to the post {report.report_to.title} has been rejected. Reason : {instance.note}."
            elif reported_object == 'Comment':
                content = f"Your report to the comment of {report.report_to.commenter.username} has been rejected. Reason : {instance.note}."
        
        try:
            create_notification(ReportContent,instance,instance.report_by,content,'Update')
        except:
            pass

@receiver(post_save,sender=ReportContent)
def report_status(instance,created,*args,**kwargs):
    if created:
        reported_object = instance.report_to.__class__.__name__
        if reported_object == 'Post':
            content = f"Your report to the post {instance.report_to.title} is under review."
        elif reported_object == 'Comment':
            content = f"Your report to the comment of {instance.report_to.commenter.username} is under review."
        else:
            pass
        try:
            create_notification(ReportContent,instance,instance.report_by,content,'Update')
        except:
            pass
    else:
        pass


        

