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

def referel_url(request):
    return request.META['HTTP_REFERER']

def comment_page(objects,object):   #Look for a page where a specific comment exist
    page_of_comment = 0
    paginator = Paginator(objects,1)
    for page in paginator:  #Find the page number where the comment available
        for comment in page:
            if comment == object:
                page_of_comment = page.number
            elif comment.get_descendants().exists():
                for child in comment.get_children():
                    if child == object:
                        page_of_comment = page.number
                    else:
                        pass
            else:
                pass
    return page_of_comment

#writing views
#home page of blog to show posts

def test(request):
    post = Post.objects.all()
    return render(request,'_Blog/test.html',{'post':post})

def index(request):
    if request.GET.get('query',None):
        query = request.GET.get('query',None)
        posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),is_deleted=False,title__contains=query)
        return render(request,'_Blog/client/index.html',{'posts':posts})
    else:
        posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),is_deleted=False)
        return render(request,'_Blog/client/index.html',{'posts':posts})

def dashboard(request):
    return render(request,'_Blog/dashboard/dashboard.html')

def list_post(request):
    page_number = int(request.GET.get('page',1))
    post = Post.objects.filter(is_deleted=False)
    paginator = Paginator(post,10.3)
    page = paginator.get_page(page_number)
    list_page = page.paginator.get_elided_page_range(number=page.number,on_each_side=2,on_ends=1)
    return render(request,"_Blog/dashboard/list_post.html",{'page':page,'list_page':list_page})


#validating & saving written post
def write_post(request):
    if request.method == "POST":

        title = request.POST.get('title','0')
        description = request.POST.get('description','0')
        cover_photo = request.FILES.get('cover_photo',None)
        content = request.POST.get('content',None)
        status = request.POST.get('status',"Draft")
        author = request.user
        tags = tuple(request.POST.getlist('tags',()))

        if request.user.rank == 'Contributor':
            if status == "Published":
                status = 'Pending'
                messages.success(request,"Your post has been successfully submitted & under review. You will get notified about status after review.")
            else:
                pass
        try:
            category = Category.objects.get(pk=int(request.POST.get('category',None)))
        except Exception as error:
            response = {"status":"error","message":"Unable to find category you selected!"}
            return HttpResponse(json.dumps(response))       

        if 5 > len(title) > 255 :
            return HttpResponse(json.dumps({"status":"error","message":"Your post title should not be blank and more than 255 character."}))
        elif len(title) > 254:
            return HttpResponse(json.dumps({"status":"error","message":"Your post title is too long."}))
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
        elif len(description) > 255 :
            return HttpResponse(json.dumps({"status":"error","message":"Your post description should not be more than 255 character."}))
        elif not status in ['Draft','Published','Pending']:
            return HttpResponse(json.dumps({"status":"error","message":"Your selected post status is not seems valid."}))
        else:
            pass
        
        new_post = Post.objects.create(title=title,description=description,cover_photo=cover_photo,content=content,category=category,author=author,status=status)
        new_post.tags.add(*tags)
        new_post.save()
        messages.success(request,"Your post has been successfully added. Now you are in edit mode.")
        edit_post_url = root_url(request) +str(reverse('Blog:edit_post', args = [new_post.hash_id] ))
        response = {"status":"success","message":"Post has been saved successfully",'destination':edit_post_url}
        return HttpResponse(json.dumps(response))
    else:
        category = Category.objects.filter(level=0)
        tags = Tag.objects.all()
        return render(request,'_Blog/dashboard/write_post.html',{'category':category,'tags':tags})
        
#sending the post instance to be rendered in details
def view_post(request,cat,slug):
    try:
        category = Category.objects.get(slug=cat)
    except:
        category = None
    user = request.user if request.user.is_authenticated else None
    try:
        post = Post.objects.get(category=category,slug=slug,is_deleted=False)
    except:
        raise Http404('No post found.')
    
    if post.status not in ['Published','Hot'] and post.author == user:
        messages.success(request,"This post preview just for you nobody else can see that until this is published.")
    elif post.status in ['Published','Hot']:
        pass
    else:
        raise Http404('No post found.')
    
    
    if request.method == "GET":
        page_number = int(request.GET.get('comment_page',1))
        comments = Comment.objects.filter(post=post,is_deleted=False,level=0).order_by('-date')
        #comment_paginator = Paginator(comments,10,2)
        comment_paginator = Paginator(comments,1)
        comment_page = comment_paginator.get_page(page_number)
        return render(request,"_Blog/client/read_post.html",{'post':post,'comment_page':comment_page,})

#fetch post to be displayed in blog by jquery
def fetch_post(request,hash_id):
    if request.method == "POST":
        try:
            post = Post.objects.get(hash_id=hash_id,is_deleted=False)
            if post.author == request.user:
                return HttpResponse(post.content)
            elif post.status in ['Published','Hot']:
                return HttpResponse(post.content)
            else: 
                return HttpResponse("...")
        except:
            return HttpResponse("No valid post found with your query.")
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
def edit_post(request,hash_id):

    try:
        _post = Post.objects.get(hash_id=hash_id,is_deleted=False)
    except:
        raise Http404


    if request.method == "POST":
        
        if _post.status == 'Pending':
            return HttpResponse(json.dumps({"status":"error","message":"While your post are pending under review. You can't make any change for now. Not even by manupulate the request."}))
        elif _post.status == 'Rejected':
            return HttpResponse(json.dumps({"status":"error","message":"While your post are rejected. You can't make any change for now. Not even by manupulate the request."}))

        title = request.POST.get('title','0')
        description = request.POST.get('description','0')
        cover_photo = request.FILES.get('cover_photo',None)
        content = request.POST.get('content',None)
        status = request.POST.get('status',"Draft")
        author = request.user
        tags = tuple(request.POST.getlist('tags',()))
        feadback_msg = None

        if request.user.rank == 'Contributor':
            if status == "Published":
                status = 'Pending'
                feadback_msg = "Your post has been successfully edited & under review. You will get notified about status after review."
            else:
                pass
        try:
            category = Category.objects.get(pk=int(request.POST.get('category',None)))
        except Exception as error:
            response = {"status":"error","message":"Unable to find category you selected!"}
            return HttpResponse(json.dumps(response))       

        if 5 > len(title) > 255 :
            return HttpResponse(json.dumps({"status":"error","message":"Your post title should not be blank and less than 255 character."}))
        elif cover_photo:
            try:
                Image.open(cover_photo)
            except:
                return HttpResponse(json.dumps({"status":"error","message":"Thanks for try to upload not an image or any payload."}))
        elif not cover_photo and not _post.cover_photo:
            return HttpResponse(json.dumps({"status":"error","message":"Where is the cover image?"}))
        elif not category:
            return HttpResponse(json.dumps({"status":"error","message":"Did you forgot to categorize your post!"}))
        elif not content:
            return HttpResponse(json.dumps({"status":"error","message":"Your forgot your aim. Where to the content?"}))
        elif len(description) > 255 :
            return HttpResponse(json.dumps({"status":"error","message":"Your post description should not be more than 255 character."}))
        elif not status in ['Draft','Published','Pending']:
            return HttpResponse(json.dumps({"status":"error","message":"Your selected post status is not seems valid."}))
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
        if not feadback_msg:
            feadback_msg = "Your post have been successfully edited."
        response = {"status":"success","message":feadback_msg}
        return HttpResponse(json.dumps(response))
    else:
        is_delete = request.GET.get('delete',False)
        if is_delete == 'true':
            _post.is_deleted = True
            _post.save()
            messages.success(request,f"Your post titled '{_post.title}' has been deleted.")
            return redirect(reverse('Blog:list_post'))
        elif _post.status == 'Pending':
            messages.error(request,"While your post are pending under review. You can't make any change for now.")
            return render(request,'_Blog/dashboard/edit_post.html',{'post':_post})
        elif _post.status == 'Rejected':
            messages.error(request,"While your post are rejected. You can't make any change for now.")
            return render(request,'_Blog/dashboard/edit_post.html',{'post':_post})
        else:
            post = Post.objects.get(pk=id)
            category = Category.objects.filter(level=0)
            tags = Tag.objects.all()
            if post.author == request.user or request.user.is_superuser:
                return render(request,'_Blog/dashboard/edit_post.html',{'category':category,'tags':tags,'post':post})
            else:
                return render(request,'_Blog/dashboard/edit_post.html',{'status':"Alert",'message':'You are not permitted to edit the post'})
    
#Notification page
def get_notification_page(user,page,type=None):
    try:
        if type:
            notifications = Notification.objects.filter(user=user,type=type)
        else:
            notifications = Notification.objects.filter(user=user)
        notifications_page = Paginator(notifications,30,5)
        current_page = notifications_page.get_page(page)
    except:
        current_page = []

    return current_page

def notifications(request):
    page = request.GET.get('page',1)
    read = request.GET.get('read',None)
    notification_category = ['Like','Comment','Follow','Update','Notice']
    if read and read in notification_category:
        notification_to_make_read = Notification.objects.filter(user=request.user,read_time=None,type=read)
        total_unread = len(notification_to_make_read)
        notification_to_make_read.update(read_time=datetime.datetime.now())
        if total_unread:
            messages.success(request,f'Your {total_unread} {read} marked as read.')
        else:
            messages.success(request,f'Your all comments are already marked as read.')
    elif read and read == 'All':
        notification_to_make_read = Notification.objects.filter(user=request.user,read_time=None)
        total_unread = len(notification_to_make_read)
        notification_to_make_read.update(read_time=datetime.datetime.now())
        if total_unread:
            messages.success(request,f'Your all {total_unread} notifications marked as read.')
        else:
            messages.success(request,f'Your all notifications are already marked as read.')
    else:
        pass

    user = request.user
    all = get_notification_page(user,page)
    like = get_notification_page(user,page,'Like')
    comment = get_notification_page(user,page,'Comment')
    follow = get_notification_page(user,page,'Follow')
    update = get_notification_page(user,page,'Update')
    notice = get_notification_page(user,page,'Notice')
    
    list_page = all.paginator.get_elided_page_range(number=all.number,on_each_side=2,on_ends=1)
    
    context = {
        'like': like,
        'comment' : comment,
        'follow' : follow,
        'update' : update,
        'notice' : notice,
        'page':all,
        'list_page':list_page
        }
    return render(request,"_Blog/dashboard/notifications.html",context)

#Create link for notification
def notification_link(request,hash_id):
    try:
        notification = Notification.objects.get(user=request.user,hash_id=hash_id)
    except:
        messages.error(request,'There are have no such notification found.')
        return redirect(reverse('Blog:notifications'))
    if notification.type == 'Comment':
        post = notification.content_object.post
        comments = Comment.objects.filter(post=post,is_deleted=False,level=0).order_by('-date')
        page_of_comment = comment_page(comments,notification.content_object) #get the comment page
        post_url = reverse('Blog:read_post',args=[post.category.slug,post.slug])
        url_to_redirect = f"{post_url}?comment_page={page_of_comment}#comment-{notification.content_object.hash_id.hex}"
    elif notification.type == 'Like':
        post = notification.content_object
        url_to_redirect = reverse('Blog:read_post',args=[post.category.slug,post.slug])
    elif notification.type == 'Follow':
        messages.error(request,"The notification doesn't linked with anything.")
        url_to_redirect = referel_url(request)
    elif notification.type == 'Update':
        messages.error(request,"The notification doesn't linked with anything.")
        url_to_redirect = referel_url(request)
    elif notification.type == 'Notice':
        messages.error(request,"The notification doesn't linked with anything.")
        url_to_redirect = referel_url(request)
    else:
        pass
    notification.read_time = datetime.datetime.now() #Mark the notification as read
    notification.save()
    return redirect(url_to_redirect)
    
#Comment handler
def comment(request,phash,chash):
    #Initializing variables
    referer_url = request.META['HTTP_REFERER']
    user = request.user if request.user.is_authenticated else None
    
    try:
        post = Post.objects.filter(Q(status='Published')|Q(status='Hot'),hash_id=phash,is_deleted=False)[0]
    except:
        messages.error(request,"No published post found to comment.")
        return redirect(f"{referer_url}#feadback")
    
    if chash == '0':
        comment = None
    else:
        try:
            comment = Comment.objects.filter(hash_id=chash,post=post)[0]
        except:
            messages.error(request,"No comment found with the id.")
            return redirect(f"{referer_url}#feadback")

    

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
                    ReportContent.objects.create(type='Comment',content_type=ContentType.objects.get_for_model(Comment),content_id=comment.pk,report_by=user,report_content=report_content)
                    messages.success(request,"Your report has been sent to admin. and you will get notified when the issue will be solved.")
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
                    return redirect(f"{referer_url}#comment-{comment.hash_id.hex}")
                else:
                    new_comment = Comment.objects.create(post=post,parent=comment,commenter=user,content=comment_content,status="Published")
                    messages.success(request,"Your reply have been added successfully.")
                    return redirect(f"{referer_url}#comment-{new_comment.hash_id.hex}")
            else:
                new_comment = Comment.objects.create(post=post,commenter=user,content=comment_content,status="Published")
                messages.success(request,"Your comment have been added successfully.")
                post_url = reverse('Blog:read_post',args=[post.category.slug,post.slug])
                return redirect(f"{post_url}#comment-{new_comment.hash_id.hex}")
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
    

#Report pages
def get_report_page(page,type=None):
    try:
        if type:
            reports = ReportContent.objects.filter(type=type)
        else:
            reports = ReportContent.objects.filter()
        reports_page = Paginator(reports,3)
        current_page = reports_page.get_page(page)
    except:
        current_page = []

    return current_page

#Generate link of report content
def report_link(request,hash_id):
    try:
        report = ReportContent.objects.get(hash_id=hash_id)
    except:
        messages.error(request,'There are have no such notification found.')
        return redirect(reverse('Blog:reports'))
    if request.method ==  'POST':
        status = request.POST.get('status','Pending')
        reason = request.POST.get('reason','')
        if status in ['Solved','Rejected']:
            report.status = status
            report.note = reason
            report.save()
            messages.success(request,f'The report has been marked as {status}.')
        else:
            pass
        return redirect(referel_url(request))
    else:
        if report.type == 'Comment':
            comment = report.report_to
            comments = Comment.objects.filter(post=comment.post,is_deleted=False,level=0).order_by('-date')
            page_of_comment = comment_page(comments,comment) #get the comment page
            post_url = reverse('Blog:read_post',args=[comment.post.category.slug,comment.post.slug])
            url_to_redirect = f"{post_url}?comment_page={page_of_comment}#comment-{report.report_to.hash_id.hex}"
        elif report.type == 'User':
            user = report.report_to.username
            messages.error(request,f"The user page for {user} under build.")
            url_to_redirect = referel_url(request)
        elif report.type == 'Post':
            post = report.report_to
            url_to_redirect = reverse('Blog:read_post',args=[post.category.slug,post.slug])
        else:
            messages.error(request,"The notification doesn't linked with anything.")
            url_to_redirect = referel_url(request)
            
        return redirect(url_to_redirect)

#Saving report for further review
def reports(request):
    if request.method == 'POST':
        pass
    else:
        page = request.GET.get('page',1)
        all = get_report_page(page,)
        comment = get_report_page(page,'Comment')
        post = get_report_page(page,'Post')
        user = get_report_page(page,'User')
        other = get_report_page(page,'Other')
        
        list_page = all.paginator.get_elided_page_range(number=all.number,on_each_side=2,on_ends=1)

        context = {
            'page' : all,
            'comment' : comment,
            'post' : post,
            'user' : user,
            'other' : other,
            'list_page' : list_page
        }
        return render(request,'_Blog/dashboard/reports.html',context)