from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, m2m_changed, pre_delete
from django.contrib.contenttypes.models import ContentType
from Blog.models import *
import os


#Additional function
def create_notification(model,instance,user,content,type):
    notification = Notification(content_type=ContentType.objects.get_for_model(model),content_id=instance.id,user=user)
    notification.content = content
    notification.type = type
    notification.save()
#Notification to follower
def notification_to_follower(model,instance,user,content,type):
    follower = user.follower.all()
    for fan in follower:
        if user not in fan.mute_list.all():
            notification = Notification(content_type=ContentType.objects.get_for_model(model),content_id=instance.id,user=fan)
            notification.content = content
            notification.type = type
            notification.save()


#get display name for the user 
def get_display_name(user):
    if user.first_name or user.last_name:
        return f"{user.first_name} {user.last_name}"
    else:
        return user.username
    

#Notification for comment & reply
@receiver(post_save,sender=Comment)
def new_comment(instance,created,*args,**kwargs):
    if instance.commenter:
        commenter = instance.commenter.username
    else:
        commenter = "Anonymous"
    if created and instance.commenter != instance.post.author:
        if instance.level == 0:
            content = f"{commenter} commented on your post '{instance.post.title}' >> \n{instance.content[:20]}"
            create_notification(Comment,instance,instance.post.author,content,'Comment')
        elif instance.level != 0 and instance.commenter != instance.parent.commenter:
            replied_comment = instance.parent
            content = f"{commenter} replied to your comment on the post '{instance.post.title}' >> \n {instance.content[:20]}"
            create_notification(Comment,instance,replied_comment.commenter,content,'Comment')
    else:
        pass

#Notification after review a post
@receiver(pre_save,sender=Post)
def post_status(instance,*args,**kwargs):
    if instance.pk:
        post = Post.objects.get(pk=instance.pk)
        if post.note != instance.note:
            reason = f"Note: {instance.note}"
        else:
            reason = ''

        if post.status in ['Draft','Rejected','Pending'] and instance.status in 'Published':
            content = f"Your post {instance.title} has been Published."
            create_notification(Post,instance,instance.author,content,'Update')
            follower_content = f"{get_display_name(instance.author)} published a new post {instance.title}."
            notification_to_follower(Post,instance,instance.author,follower_content,'Update')
        elif post.status != 'Hot' and instance.status == 'Hot':
            content = f"Your post {instance.title} has been choosen as hot post."
            create_notification(Post,instance,instance.author,content,'Update')
            follower_content = f"{get_display_name(instance.author)}'s post is been marked as hot {instance.title}."
            notification_to_follower(Post,instance,instance.author,follower_content,'Update')
        elif post.status != 'Pending' and instance.status == 'Pending':
            content = f"Your post {instance.title} is now under review."
            create_notification(Post,instance,instance.author,content,'Update')
        elif post.status == 'Pending' and instance.status == 'Rejected':
            content = f"Your post {instance.title} has been rejected. {reason}"
            create_notification(Post,instance,instance.author,content,'Notice')

    else:
        pass

#Notification if any user role changed or author applicaion approved
@receiver(pre_save,sender=AuthorUser)
def user_status(sender,instance,*args,**kwargs):
    role = ["Banned","Contributor","Author","Moderator","Admin"]
    if instance.pk:
        user = sender.objects.get(pk=instance.pk)
        
        if user.note != instance.note:
            reason = f"Note: {instance.note}"
        else:
            reason = ''
            
        if user.rank != 'Banned' and instance.rank == 'Banned':
            content = f"Dear {instance.username}, You are now banned. {reason}"
            create_notification(sender,instance,instance,content,'Notice') 
        elif role.index(user.rank) < role.index(instance.rank):
            content = f"Dear {instance.username}, Your rank updated from {user.rank} to {instance.rank}."
            create_notification(sender,instance,instance,content,'Update')
        elif role.index(user.rank) > role.index(instance.rank):
            content = f"Dear {instance.username}, Your rank downgraded from {user.rank} to {instance.rank}."
            create_notification(sender,instance,instance,content,'Notice')
        else:
            pass
    else:
        pass

#Notification when a user report reviewed
@receiver(pre_save,sender=ReportContent)
def report_status_reviewed(sender,instance,*args,**kwargs):
    if instance.pk:
        report_type = instance.type
        report = sender.objects.get(pk=instance.pk)
        
        if report.note != instance.note:
            reason = f"Note: {instance.note}"
        else:
            reason = ''
            
        if report.status != 'Solved' and instance.status == 'Solved':
            if report_type == 'Post':
                content = f"Your report to the post {report.report_to.title} has been solved. {reason}"
            elif report_type == 'Comment':
                content = f"Your report to the comment of {report.report_to.commenter.username} has been solved. {reason}"
            elif report_type == 'User':
                content = f"Your report to the user {report.report_to.username} has been solved. {reason}"
        if report.status != 'Rejected' and instance.status == 'Rejected':
            if report_type == 'Post':
                content = f"Your report to the post {report.report_to.title} has been rejected. {reason}"
            elif report_type == 'Comment':
                content = f"Your report to the comment of {report.report_to.commenter.username} has been rejected. {reason}"
            elif report_type == 'User':
                content = f"Your report to the user {report.report_to.username} has been rejected. {reason}"
        
        try:
            create_notification(ReportContent,instance,instance.report_by,content,'Update')
        except:
            pass

#Notification for who submitted a report agaist any post or comment.
@receiver(post_save,sender=ReportContent)
def report_status(instance,created,*args,**kwargs):
    if created:
        report_type = instance.type
        if report_type == 'Post':
            content = f"Your report to the post {instance.report_to.title} is under review."
        elif report_type == 'Comment':
            content = f"Your report to the comment of {instance.report_to.commenter.username} is under review."
        else:
            pass
        try:
            create_notification(ReportContent,instance,instance.report_by,content,'Notice')
        except:
            pass
    else:
        pass

#Notification when someone follow someone.
@receiver(m2m_changed, sender=AuthorUser.follower.through)
def notify_user_followed(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add' and not reverse:
        # Get the newly added followers
        new_followers = model.objects.filter(pk__in=pk_set)

        for follower in new_followers:
            try:
                if not instance in follower.mute_list.all():
                    content = f"{follower.display_name()} started following you."
                    create_notification(AuthorUser,follower,instance,content,'Follow')
            except:
                pass

#Notification when someone liked a post.
@receiver(m2m_changed, sender=Post.like.through)
def notify_user_followed(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add' and not reverse:
        # Get the newly added followers
        new_like = model.objects.filter(pk__in=pk_set)

        for liker in new_like:
            try:
                if not liker in instance.author.mute_list.all():
                    content = f"{liker.display_name()} liked your post titled {instance.title}."
                    create_notification(Post,liker,instance.author,content,'Like')
            except:
                pass

#Delete uploaded image when model instance deleted
@receiver(pre_delete, sender=UploadedImages)
def delete_uploadedimage(sender, instance, **kwargs):
    # Get the path to the image file
    image_path = instance.image.path

    # Check if the file exists and delete it
    if os.path.isfile(image_path):
        os.remove(image_path)

#Delete user profile photo when model instance deleted
@receiver(pre_delete, sender=AuthorUser)
def delete_userprofile(sender, instance, **kwargs):
    # Get the path to the image file
    image_path = instance.profile_photo.path

    # Check if the file exists and delete it
    if os.path.isfile(image_path):
        os.remove(image_path)

        

