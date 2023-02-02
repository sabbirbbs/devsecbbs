#import modules
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from .models import *
from .forms import *
from PIL import Image
import json
from taggit.models import Tag
import datetime
from django.db.models import Q
import os
import re


#Additional variable
app_dir = os.path.dirname(__file__)  # get current directory




#Additional Function
#Filter bad words from content
def filter_content(value):
    bad_words = set()
    with open(os.path.join(app_dir, 'afiles/badwords.txt'),"r") as blist:
        listi = blist.read().lower().split(",")
        value = set(re.sub("[^\w]", " ", value.lower()).split())
        for word in listi:
            if word in value:
                bad_words.add(word)
            else:
                pass
    return list(bad_words)

#writing views
#home page of blog to show posts
def index(request):
    posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),is_deleted=False)
    #return render(request,"blog/blog_page.html",{"posts":posts})
    return render(request,'_Blog/index.html',{'posts':posts})

#validating & saving written post
def write_post(request):
    if request.method == "POST":

        title = request.POST.get('title',None)
        description = request.POST.get('description',None)
        cover_photo = request.FILES.get('cover_photo',None)
        content = request.POST.get('content',None)
        status = request.POST.get('status',"Draft")
        author = request.user
        category = Category.objects.get(pk=int(request.POST.get('category',1)))
        tags = tuple(request.POST.getlist('tags',()))

        if not title:
            return HttpResponse(json.dumps({"status":"info","message":"Where is the title"}))
        elif cover_photo:
            try:
                Image.open(cover_photo)
            except:
                return HttpResponse(json.dumps({"status":"info","message":"Thanks for try to upload not an image or any payload."}))
        elif not cover_photo:
            return HttpResponse(json.dumps({"status":"info","message":"Where is the cover image"}))
        elif not category:
            return HttpResponse(json.dumps({"status":"info","message":"Did you forgot to categorize your post!"}))
        elif not content:
            return HttpResponse(json.dumps({"status":"info","message":"At least add the title to the content.Why blank?"}))
        else:
            pass
        
        new_post = Post.objects.create(title=title,description=description,cover_photo=cover_photo,content=content,category=category,author=author,status=status)
        new_post.tags.add(*tags)
        new_post.save()
        response = {"status":"success","message":"Post has been saved successfully"}
        return HttpResponse(json.dumps(response))
    else:
        category = Category.objects.filter(level=0)
        tags = Tag.objects.all()
        return render(request,'blog/write_post.html',{'category':category,'tags':tags})
        
#sending the post instance to be rendered in details
def view_post(request,cat,slug):
    post = Post.objects.get(Q(status="Published")|Q(status="Hot"),slug=slug,is_deleted=False)
    return render(request,"blog/read_post.html",{'post':post})

#fetch post to be displayed in blog by jquery
def fetch_post(request,pk):
    if request.method == "POST":
        post = Post.objects.get(Q(status="Published")|Q(status="Hot"),pk=pk,)
        return HttpResponse(post.content)
    else:
        pass

#show posts by category
def category(request,slug):
    category = Category.objects.get(slug=slug).get_descendants(include_self=True)
    posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),category__in=category)
    return render(request,"blog/category_post.html",{"posts":posts,"category":category})

#show posts by tags
def tag(request,slug):
    posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),tags__slug=slug)
    return render(request,"blog/tag_post.html",{"posts":posts,"tag":slug})

#Post edit
def edit_post(request,id):
    if request.method == "POST":

        title = request.POST.get('title',None)
        description = request.POST.get('description',None)
        cover_photo = request.FILES.get('cover_photo',None)
        content = request.POST.get('content',None)
        status = request.POST.get('status',"Draft")
        author = request.user
        category = Category.objects.get(pk=int(request.POST.get('category',1)))
        tags = tuple(request.POST.getlist('tags',()))

        if not title:
            return HttpResponse(json.dumps({"status":"info","message":"Where is the title"}))
        elif cover_photo:
            try:
                Image.open(cover_photo)
            except:
                return HttpResponse(json.dumps({"status":"info","message":"Thanks for try to upload not an image or any payload."}))
        elif not category:
            return HttpResponse(json.dumps({"status":"info","message":"Did you forgot to categorize your post!"}))
        elif len(content) < 50:
            return HttpResponse(json.dumps({"status":"info","message":"Is that is the content of post? At least add some lorem ipsum!"}))
        else:
            pass
        _post  = Post.objects.get(pk=id)
        _post.title = title
        _post.description = description
        _post.content = content
        _post.category = category
        _post.author = author
        _post.status = status
        _post.last_modified = datetime.datetime.now()
        if cover_photo:
            _post.cover_photo = cover_photo
        else:
            pass
        _post.tags.add(*tags)
        _post.save()
        response = {"status":"success","message":"Post has been edited successfully"}
        return HttpResponse(json.dumps(response))
    else:
        post = Post.objects.get(pk=id)
        category = Category.objects.filter(level=0)
        tags = Tag.objects.all()
        if post.author == request.user or request.user.is_superuser:
            return render(request,'blog/edit_post.html',{'category':category,'tags':tags,'post':post})
        else:
            return render(request,'blog/edit_post.html',{'status':"Alert",'message':'You are not permitted to edit the post'})
    

def notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    notifications.update(read_time=datetime.datetime.now())
    return render(request,"blog/notifications.html",{"notifications":notifications[:50]})

def comment(request,pid,cid):
    if request.method == "POST":
        post = Post.objects.get(pk=pid)
        
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        try:
            comment = Comment.objects.get(pk=cid,post=post)
        except Exception as error:
            comment = None

        content = request.POST.get("comment",None)
        if content:
            if filter_content(content):
                response = {"status":"alert","message":f"Sorry, Your comment can't be published cause of those word! {filter_content(content)}"}
                return HttpResponse(json.dumps(response))
            elif len(content) < 2 or len(content) > 255:
                response = {"status":"Notice","message":"Your comment have to be in between 1-255 character!"}
                return HttpResponse(json.dumps(response))
        else:
            response = {"status":"Notice","message":"Seems your comment is empty!"}
            return HttpResponse(json.dumps(response))

                
        if comment:
            comment = Comment.objects.create(post=post,parent=comment,commenter=user,content=content,status="Published")
            response = {"status":"success","message":"Your reply has been successfully added."}
            return HttpResponse(json.dumps(response))
        else:
            comment = Comment.objects.create(post=post,commenter=user,content=content,status="Published")
            response = {"status":"success","message":"Comment has been successfully added."}
            return HttpResponse(json.dumps(response))
    else:
        response = {"status":"alert","message":"Invalid gateway!"}
        return HttpResponse(json.dumps(response))