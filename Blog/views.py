#import modules
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from .forms import *
from PIL import Image
import json
from taggit.models import Tag
import datetime
from django.db.models import Q



#writing views
#home page of blog to show posts
def index(request):
    posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),is_deleted=False)
    return render(request,"blog/blog_page.html",{"posts":posts})

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
    category = Category.objects.get(slug=slug)
    posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),category=category)
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
