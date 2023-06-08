#import modules
from django.db import models
import datetime
import os
import time
import random
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
import re
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid
from django.db.models import Q

#Slugify unicode bangla text
def unislug(value,unique=False):
    """This will just remove whitespace & lower the value to make it slugi"""
    forbid_char = [":", "/", "?", "#", "[", "]", "@", "!", "$", "&", "'", "(", ")", "*", "+", ",", ";", "=", " "]
    value = value.lower()
    for char in forbid_char:
        value = value.replace(char,"-")
    if unique:
        pattern = r"_[0-9a-fA-F]{10}$"
        salt = uuid.uuid4().hex[:10]
        if re.search(pattern,value):
            return value.rsplit('_',1)[0] + "_" + salt
        else:
            return value + "_" + salt
    else:
        return value


#additional function

#change file name of post cover
def post_cover(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    valid_image_ext = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
    ]
    if file_extension.lower() in valid_image_ext:
        return 'blog/post_cover/{basename}_{randomstring}{ext}'.format(basename= basefilename, randomstring= time.time(), ext= file_extension.lower())
    else:
        return 'blog/post_cover/{basename}_{randomstring}{ext}'.format(basename= basefilename, randomstring= time.time(), ext= ".ext")

#change file name of author profile
def author_profile(instance, filename):
    basefilename, file_extension = os.path.splitext(filename)
    valid_image_ext = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
    ]
    if file_extension.lower() in valid_image_ext:
        return 'blog/author/{basename}_{randomstring}{ext}'.format(basename= instance.username, randomstring= random.randint(1,int(time.time())), ext= file_extension.lower())
    else:
        return 'blog/author/{basename}_{randomstring}{ext}'.format(basename= instance.username, randomstring= random.randint(1,int(time.time())), ext= ".ext")



#writing database models

class Category(MPTTModel):
    hash_id = models.UUIDField(unique=True,default=uuid.uuid4,editable=False)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,null=True,blank=True, related_name='children')
    name = models.CharField(max_length=255)
    slug = models.CharField(unique=True,null=True,blank=True,max_length=255)
    date = models.DateTimeField(default=datetime.datetime.now)
    is_active = models.BooleanField(default=True)
    note = models.TextField(blank=True,null=True)

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = unislug(self.name)
        else:
            self.slug = unislug(self.slug)

        return super().save(*args,**kwargs)

    def __str__(self):
        return self.name

class Post(models.Model):
    hash_id = models.UUIDField(unique=True,default=uuid.uuid4,editable=False)
    title = models.CharField(max_length=255)
    slug = models.CharField(unique=True,null=True,blank=True,max_length=255)
    description = models.CharField(max_length=255,blank=True)
    cover_photo = models.ImageField(upload_to=post_cover,default="blog/post_cover/cover.jpg")
    content = models.TextField()
    author = models.ForeignKey('AuthorUser',on_delete=models.SET_NULL,null=True,related_name="user_post")
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name="category_post")
    series = models.ForeignKey('Series',blank=True,null=True,on_delete=models.CASCADE,related_name='post_in_series')
    tags = TaggableManager(blank=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    last_modified = models.DateTimeField(default=datetime.datetime.now)
    status = models.CharField(max_length=255,choices=[("Draft","Draft"),("Published","Published"),("Hot","Hot"),("Rejected","Rejected"),("Pending","Pending")])
    is_deleted = models.BooleanField(default=False)
    note = models.TextField(blank=True,null=True)

    def get_active_comment(self):
        total_comment = 0
        for comment in self.post_comment.all(): #Count all the vaild available undeleted comments
            if comment.level == 0 and comment.is_deleted == False:
                for reply in comment.get_descendants(include_self=True):
                    if reply.is_deleted == False:
                        total_comment += 1
                    else:
                        pass
            else:
                pass
        return total_comment
    
    class Meta:
        ordering = ('-date',)

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = unislug(self.title,True)
        else:
            self.slug = unislug(self.slug)
        

        return super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.title}"

class Comment(MPTTModel):
    hash_id = models.UUIDField(unique=True,default=uuid.uuid4,editable=False)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,blank=True,null=True,related_name="post_comment")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, blank=True,null=True,related_name='children')
    commenter = models.ForeignKey('AuthorUser',on_delete=models.SET_NULL,null=True,blank=True,related_name="user_comment")
    content = models.TextField()
    date = models.DateTimeField(default=datetime.datetime.now)
    status = models.CharField(max_length=255,choices=[("Published","Published"),("Rejected","Rejected"),("Pending","Pending")],null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    note = models.TextField(blank=True,null=True)
    
    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return str(self.content)

class AuthorUser(AbstractUser):
    hash_id = models.UUIDField(unique=True,default=uuid.uuid4,editable=False)
    profile_photo = models.ImageField(upload_to=author_profile,blank=True,null=True)
    bio = models.TextField(max_length=255,blank=True,null=True)
    rank = models.CharField(max_length=255,default="Contributor",choices=[('Contributor',"Contributor"),("Author","Author"),("Moderator","Moderator"),("Admin","Admin"),("Banned","Banned")])
    dob = models.DateTimeField(null=True,blank=True)
    gender = models.CharField(max_length=10,blank=True,null=True,choices=[("Male","Male"),("Female","Female")])
    website = models.SlugField(null=True,blank=True)
    facebook_profile = models.SlugField(null=True,blank=True)
    twitter_profile = models.SlugField(null=True,blank=True)
    github_profile = models.SlugField(null=True,blank=True)
    website_url = models.URLField(null=True,blank=True)
    country = models.CharField(max_length=255,blank=True,null=True)
    city = models.CharField(max_length=255,null=True,blank=True)
    phone = models.IntegerField(null=True,blank=True)
    series = models.ManyToManyField('Series',blank=True,related_name="user_series")
    follower = models.ManyToManyField('AuthorUser',blank=True,related_name="user_following")
    mute_list = models.ManyToManyField('AuthorUser',blank=True,related_name="muted")
    is_deleted = models.BooleanField(default=False)
    note = models.TextField(blank=True,null=True)

    def live_post(self):
        return self.user_post.filter(Q(status='Published')|Q(status='Hot'))

    class Meta:
        ordering = ('-date_joined',)

    def __str__(self):
            return f"{self.username}"

class Notification(models.Model):
    hash_id = models.UUIDField(unique=True,default=uuid.uuid4,editable=False)
    notification_type = ('Like','Comment','Follow','Update','Notice',)
    type = models.CharField(max_length=255,default=None,choices=list(zip(notification_type,notification_type)))
    user = models.ForeignKey(AuthorUser,on_delete=models.CASCADE,related_name="user_notification")
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type','content_id')
    content = models.TextField(null=True,blank=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    read_time = models.DateTimeField(blank=True,null=True)
    note = models.TextField(blank=True,null=True)

    
    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return self.content

class ReportContent(models.Model):
    hash_id = models.UUIDField(unique=True,default=uuid.uuid4,editable=False)
    report_type = ('Comment','User','Post','Other',)
    type = models.CharField(max_length=255,default='Other',choices=list(zip(report_type,report_type)))
    report_by = models.ForeignKey(AuthorUser,on_delete=models.CASCADE,related_name="user_report")
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField()
    report_to = GenericForeignKey('content_type','content_id') 
    report_content = models.TextField()
    date = models.DateTimeField(default=datetime.datetime.now)
    status = models.CharField(max_length=255,default="Pending",choices=[("Solved","Solved"),('Pending','Pending'),('Rejected','Rejected')])
    note = models.TextField(blank=True,null=True)

    
    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return f"{self.report_content}"
    
class UserRequest(models.Model):
    hash_id = models.UUIDField(unique=True,default=uuid.uuid4,editable=False)
    title = models.CharField(max_length=255)
    user = models.ForeignKey(AuthorUser,on_delete=models.CASCADE,related_name="user_request")
    content = models.TextField()
    date = models.DateTimeField(default=datetime.datetime.now)
    review_date = models.DateTimeField(blank=True,null=True)
    status = models.CharField(max_length=255,default="Pending",choices=[("Accepted","Accepted"),('Pending','Pending'),('Rejected','Rejected')])
    type = models.CharField(max_length=255,default="Other",choices=[("Author","Author"),('Other','Other'),('Request','Request')])
    note = models.TextField(blank=True,null=True)

    def __str__(self):
        return f"{self.title} by {self.user.username}"
    
class Series(models.Model):
    hash_id = models.UUIDField(unique=True,default=uuid.uuid4,editable=False)
    slug = models.CharField(unique=True,null=True,blank=True,max_length=255)
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(AuthorUser,on_delete=models.CASCADE,related_name="series_created")
    created_date = models.DateTimeField(default=datetime.datetime.now)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=255,default="Public",choices=[("Public","Public"),('Draft','Draft')])
    note = models.TextField(blank=True,null=True)


    def save(self,*args,**kwargs):
            if not self.slug:
                self.slug = unislug(self.title,True)
            else:
                self.slug = unislug(self.slug)
            

            return super().save(*args,**kwargs)
    
    def __str__(self):
        return f"{self.name} by {self.created_by.username}"

    class Meta:
        verbose_name_plural = "Series"
    
     
    



