#import modules
from django.shortcuts import render, redirect , get_object_or_404
from django.http import HttpResponse,Http404
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
from better_profanity import profanity
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator

#Additional variable
app_dir = os.path.dirname(__file__)  # get current directory




#Additional Function
def root_url(request):
    return request.scheme+"://"+request.get_host()



#writing views
#home page of blog to show posts

def test(request):
    post = Post.objects.all()
    return render(request,'_Blog/test.html',{'post':post})

def index(request):
    posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),is_deleted=False)
    return render(request,'_Blog/client/index.html',{'posts':posts})

def dashboard(request):
    return render(request,'_Blog/dashboard/dashboard.html')

def list_post(request):
    page_number = int(request.GET.get('page',1))
    post = Post.objects.filter(is_deleted=False)
    paginator = Paginator(post,10,3)
    if page_number:
        page = paginator.get_page(page_number)
        list_page = page.paginator.get_elided_page_range(number=page.number,on_each_side=2,on_ends=1)
        return render(request,"_Blog/dashboard/list_post.html",{'page':page,'list_page':list_page})
    else:
        page = paginator.get_page(1)
        list_page = page.paginator.get_elided_page_range(number=page.number,on_each_side=2,on_ends=1)
        return render(request,"_Blog/dashboard/list_post.html",{'page':page,'list_page':list_page})


#validating & saving written post
def write_post(request):
    if request.method == "POST":

        title = request.POST.get('title',None)
        description = request.POST.get('description',None)
        cover_photo = request.FILES.get('cover_photo',None)
        content = request.POST.get('content',None)
        status = request.POST.get('status',"Draft")
        author = request.user
        try:
            category = Category.objects.get(pk=int(request.POST.get('category',1)))
        except Exception as error:
            response = {"status":"error","message":"Did you forgot to categorize your post!"}
            return HttpResponse(json.dumps(response))
        
        tags = tuple(request.POST.getlist('tags',()))

        if not title:
            return HttpResponse(json.dumps({"status":"error","message":"Where is the title"}))
        elif title: #Check if any post already exit with the title
            title_slug = unislug(title)
            post = Post.objects.filter(slug=title_slug)[0]
            if post and (post.status == 'Published' or post.status == 'Hot'):
                post_url = root_url(request)+reverse('Blog:read_post', args=[post.category.slug,post.slug])
                return HttpResponse(json.dumps({"status":"error","message":"A post with the same title may already posted. "+f'<u><a href="{post_url}" target="_blank">{post.title}</a></u>'}))
            elif post:
                return HttpResponse(json.dumps({"status":"error","message":"A post with the same title already in someone draft."}))
            else:
                pass

        elif cover_photo:
            try:
                Image.open(cover_photo)
            except:
                return HttpResponse(json.dumps({"status":"error","message":"Thanks for try to upload not an image or any payload."}))
        elif not cover_photo:
            return HttpResponse(json.dumps({"status":"error","message":"Where is the cover image?"}))
        elif not category:
            return HttpResponse(json.dumps({"status":"error","message":"Did you forgot to categorize your post!"}))
        elif not content:
            return HttpResponse(json.dumps({"status":"error","message":"Your forgot your aim. Where to the content?"}))
        else:
            pass
        
        new_post = Post.objects.create(title=title,description=description,cover_photo=cover_photo,content=content,category=category,author=author,status=status)
        new_post.tags.add(*tags)
        new_post.save()
        messages.success(request,"Your post has been successfully added. Now you are in edit mode.")
        edit_post_url = root_url(request) +str(reverse('Blog:edit_post', args = [new_post.pk] ))
        response = {"status":"success","message":"Post has been saved successfully",'destination':edit_post_url}
        return HttpResponse(json.dumps(response))
    else:
        category = Category.objects.filter(level=0)
        tags = Tag.objects.all()
        return render(request,'_Blog/dashboard/write_post.html',{'category':category,'tags':tags})
        
#sending the post instance to be rendered in details
def view_post(request,cat,slug):
    category = Category.objects.get(slug=cat)
    post = Post.objects.get(Q(status="Published")|Q(status="Hot"),category=category,slug=slug,is_deleted=False)
    total_comment = 0
    for comment in post.post_comment.all(): #Count all the vaild available undeleted comments
        if comment.level == 0 and comment.is_deleted == False:
            for reply in comment.get_descendants(include_self=True):
                if reply.is_deleted == False:
                    total_comment += 1
                else:
                    pass
        else:
            pass

    return render(request,"_Blog/client/read_post.html",{'post':post,'total_comment':total_comment})

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

    try:
        _post = Post.objects.get(pk=id,is_deleted=False)
    except:
        raise Http404

    if request.method == "POST":        

        title = request.POST.get('title',None)
        description = request.POST.get('description',None)
        cover_photo = request.FILES.get('cover_photo',None)
        content = request.POST.get('content',None)
        status = request.POST.get('status',"Draft")
        author = request.user
        try:
            category = Category.objects.get(pk=int(request.POST.get('category',1)))
        except Exception as error:
            response = {"status":"error","message":"Did you forgot to categorize your post!"}
            return HttpResponse(json.dumps(response))
        
        tags = tuple(request.POST.getlist('tags',()))

        if not title:
            return HttpResponse(json.dumps({"status":"error","message":"Where is the title"}))
        elif title: #Check if any post already exit with the title
            title_slug = unislug(title)
            post = Post.objects.filter(slug=title_slug)[0]
            if title_slug == _post.slug:
                pass
            else:
                if post and (post.status == 'Published' or post.status == 'Hot'):
                    post_url = root_url(request)+reverse('Blog:read_post', args=[post.category.slug,post.slug])
                    return HttpResponse(json.dumps({"status":"error","message":"A post with the same title may already posted. "+f'<u><a href="{post_url}" target="_blank">{post.title}</a></u>'}))
                elif post:
                    return HttpResponse(json.dumps({"status":"error","message":"A post with the same title already in someone draft."}))
                else:
                    pass
        elif cover_photo:
            try:
                Image.open(cover_photo)
            except:
                return HttpResponse(json.dumps({"status":"error","message":"Thanks for try to upload not an image or any payload."}))
        elif not category:
            return HttpResponse(json.dumps({"status":"error","message":"Did you forgot to categorize your post!"}))
        elif len(content) < 50:
            return HttpResponse(json.dumps({"status":"error","message":"Is that is the content of post? At least add some lorem ipsum!"}))
        elif not post.author == request.user or request.user.is_superuser:
            return render(request,'_Blog/dashboard/edit_post.html',{'status':"error",'message':'You are not permitted to edit the post'})
        else:
            pass
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
        is_delete = request.GET.get('delete',False)
        if is_delete == 'true':
            _post.is_deleted = True
            _post.save()
            messages.success(request,f"Your post titled '{_post.title}' has been deleted.")
            return redirect(reverse('Blog:list_post'))
        else:
            post = Post.objects.get(pk=id)
            category = Category.objects.filter(level=0)
            tags = Tag.objects.all()
            if post.author == request.user or request.user.is_superuser:
                return render(request,'_Blog/dashboard/edit_post.html',{'category':category,'tags':tags,'post':post})
            else:
                return render(request,'_Blog/dashboard/edit_post.html',{'status':"Alert",'message':'You are not permitted to edit the post'})
    

def notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    notifications.update(read_time=datetime.datetime.now())
    return render(request,"blog/notifications.html",{"notifications":notifications[:50]})

#Comment handler
def comment(request,pid,cid):
    #Initializing variables
    post = get_object_or_404(Post,pk=pid)
    user = request.user if request.user.is_authenticated else None
    comment = Comment.objects.get(pk=cid,post=post) if Comment.objects.filter(pk=cid,post=post).exists() else None
    referer_url = request.META['HTTP_REFERER']
    if request.method == "POST":
        report_content = request.POST.get("report",None)
        comment_content = request.POST.get("comment",None)
        comment_delete = request.POST.get("comment_delete",None)
        comment_edit = request.POST.get("comment_edit",None)
        if report_content: #Handling comment report if it's in post form
            if user and user != comment.commenter:
                if 1 > len(report_content) > 255:
                    messages.error(request,"Your report is have to more than single character & less than 255.")
                    return redirect(f"{referer_url}#feadback")
                else:
                    ReportContent.objects.create(content_type=ContentType.objects.get_for_model(Comment),content_id=comment.pk,report_by=user,report_content=report_content)
                    messages.success(request,"Your reported has been sent to admin. and you will get notified when the issue will be solved.")
                    return redirect(f"{referer_url}#feadback")
            else:
                messages.error(request,"You can't report your own comment or you may not logged in!")
                return redirect(f"{referer_url}#feadback")

        elif comment_content:   #Handling comment & reply if comment content exit
            if comment_content and len(comment_content) < 500:
                comment_content = profanity.censor(comment_content) #censoring bad word from comment
            else:
                messages.error(request,"Your comment have to be in between 1-500 character!")
                return redirect(f"{referer_url}#feadback")
                    
            if comment:
                if comment_edit and comment.commenter == request.user:
                    comment.content = comment_content
                    comment.save()
                    messages.success(request,"Your comment have been edited successfully.")
                    return redirect(f"{referer_url}#comment-{comment.pk}")
                else:
                    new_comment = Comment.objects.create(post=post,parent=comment,commenter=user,content=comment_content,status="Published")
                    messages.success(request,"Your reply have been added successfully.")
                    return redirect(f"{referer_url}#comment-{new_comment.pk}")
            else:
                new_comment = Comment.objects.create(post=post,commenter=user,content=comment_content,status="Published")
                messages.success(request,"Your comment have been added successfully.")
                return redirect(f"{referer_url}#comment-{new_comment.pk}")
        elif comment_delete:
            if comment.commenter == request.user:
                comment.is_deleted = True
                comment.save()
                messages.success(request,"Your comment have been deleted successfully.")
                return redirect(f"{referer_url}#feadback")
            else:
                messages.error(request,"You don't have rights to delete the comment.")
                return redirect(f"{referer_url}#feadback")

    else:
        return HttpResponse("No parameter passed!")