#import modules
from django.db import models
import datetime
import os
import time
import random
from django.http import HttpResponse
from django.contrib.auth.models import AbstractUser,User
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
import re
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


#Slugify unicode bangla text
def unislug(value):
    """This will just remove whitespace & lower the value to make it slugi"""
    forbid_char = [":", "/", "?", "#", "[", "]", "@", "!", "$", "&", "'", "(", ")", "*", "+", ",", ";", "=", " "]
    value = value.lower()
    for char in forbid_char:
        value = value.replace(char,"-")
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
    title = models.CharField(max_length=255)
    slug = models.CharField(unique=True,null=True,blank=True,max_length=255)
    description = models.CharField(max_length=255,blank=True)
    cover_photo = models.ImageField(upload_to=post_cover,default="blog/post_cover/cover.jpg")
    content = models.TextField()
    author = models.ForeignKey('AuthorUser',on_delete=models.SET_NULL,null=True,related_name="user_post")
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name="category_post")
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
            self.slug = unislug(self.title)
        else:
            self.slug = unislug(self.slug)
        
        if self.status == "Draft" and not self.slug.endswith("_draft"):
            if self.slug.endswith("_rejected"):
                self.slug = self.slug.rsplit("_",1)[0]
            self.slug += "_draft"
        elif self.status == "Rejected" and not self.slug.endswith("_rejected"):
            if self.slug.endswith("_draft"):
                self.slug = self.slug.rsplit("_",1)[0]
            self.slug += "_rejected"

        return super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.title}"

class Comment(MPTTModel):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,blank=True,null=True,related_name="post_comment")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, blank=True,null=True,related_name='children')
    commenter = models.ForeignKey('AuthorUser',on_delete=models.SET_NULL,null=True,related_name="user_comment")
    content = models.TextField()
    date = models.DateTimeField(default=datetime.datetime.now)
    status = models.CharField(max_length=255,choices=[("Published","Published"),("Rejected","Rejected")],null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    note = models.TextField(blank=True,null=True)
    
    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return str(self.content)

class AuthorUser(AbstractUser):
    profile_photo = models.ImageField(upload_to=author_profile,blank=True,null=True)
    bio = models.CharField(max_length=255,blank=True,null=True)
    rank = models.CharField(max_length=255,choices=[('Contributor',"Contributor"),("Author","Author"),("Moderator","Moderator"),("Admin","Admin"),("Banned","Banned")])
    dob = models.DateTimeField(null=True,blank=True)
    gender = models.CharField(max_length=10,blank=True,null=True,choices=[("Male","Male"),("Female","Female")])
    website = models.SlugField(null=True,blank=True)
    facebook_profile = models.SlugField(null=True,blank=True)
    twitter_profile = models.SlugField(null=True,blank=True)
    github_profile = models.SlugField(null=True,blank=True)
    country = models.CharField(max_length=255,blank=True,null=True)
    city = models.CharField(max_length=255,null=True,blank=True)
    phone = models.IntegerField(null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    note = models.TextField(blank=True,null=True)

    
    class Meta:
        ordering = ('-date_joined',)

    def __str__(self):
            return f"{self.username}"

class Notification(models.Model):
    user = models.ForeignKey(AuthorUser,on_delete=models.CASCADE,related_name="user_notification")
    title = models.CharField(max_length=255,null=True,blank=True)
    content = models.TextField(null=True,blank=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    read_time = models.DateTimeField(blank=True,null=True)
    note = models.TextField(blank=True,null=True)

    
    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return self.title

class ReportContent(models.Model):
    report_by = models.ForeignKey(AuthorUser,on_delete=models.CASCADE,related_name="user_report")
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField()
    report_to = GenericForeignKey('content_type','content_id')
    report_content = models.TextField()
    date = models.DateTimeField(default=datetime.datetime.now)
    status = models.CharField(max_length=255,default="pending",choices=[("solved","Solved"),('pending','Pending'),('rejected','Rejected')])

    
    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return f"{self.report_content}"
