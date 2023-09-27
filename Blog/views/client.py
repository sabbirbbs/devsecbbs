#import modules
from django.shortcuts import render, redirect
from django.http import HttpResponse,Http404
from django.urls import reverse
from Blog.models import *
from taggit.models import Tag
from django.db.models import Q
from better_profanity import profanity
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from Blog.models import AuthorUser
from Blog.extrafunc import *
from Blog.token import *
import base64
import json

#home page of blog to show posts
def index(request):
    if request.GET.get('query',None):
        query = request.GET.get('query',None)
        posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),is_deleted=False,title__contains=query)
        return render(request,'_Blog/client/index.html',{'posts':posts})
    else:
        posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),is_deleted=False)
        return render(request,'_Blog/client/index.html',{'posts':posts})

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

    page = request.GET.get('post-page',1)
    try:
        post_category = Category.objects.get(slug=slug)
    except:
        raise Http404
    
    category = Category.objects.get(slug=slug).get_descendants(include_self=True)
    posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),category__in=category)
    posts_page = Paginator(posts,2)
    current_page = posts_page.get_page(page)
    list_page = current_page.paginator.get_elided_page_range(number=current_page.number,on_each_side=2,on_ends=1)
    return render(request,"_Blog/client/category_post.html",{"page":current_page,'list_page':list_page,"post_category":post_category})

#show posts by series
def series(request,slug):

    page = request.GET.get('post-page',1)
    try:
        series = Series.objects.get(slug=slug)
    except:
        raise Http404
    posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),series=series)
    posts_page = Paginator(posts,2)
    current_page = posts_page.get_page(page)
    list_page = current_page.paginator.get_elided_page_range(number=current_page.number,on_each_side=2,on_ends=1)
    return render(request,"_Blog/client/series_post.html",{"page":current_page,'list_page':list_page,'series':series})

#show posts by tags
def tag(request,slug):

    page = request.GET.get('post-page',1)
    try:
        tag = Tag.objects.get(slug=slug)
    except:
        raise Http404
    posts = Post.objects.filter(Q(status="Published")|Q(status="Hot"),tags=tag)
    posts_page = Paginator(posts,2)
    current_page = posts_page.get_page(page)
    list_page = current_page.paginator.get_elided_page_range(number=current_page.number,on_each_side=2,on_ends=1)
    return render(request,"_Blog/client/tag_post.html",{"page":current_page,'list_page':list_page,'tag':tag})
    
#sending the post instance to be rendered in details
def view_post(request,cat,slug):
    try:
        category = Category.objects.get(slug=cat)
    except:
        category = None
    user = request.user if request.user.is_authenticated else None
    try:
        if request.user == "Admin" or request.user.is_superuser:
            post = Post.objects.get(category=category,slug=slug)
        else:
            post = Post.objects.get(category=category,slug=slug,is_deleted=False)
    except:
        raise Http404('No post found.')
    
    if post.status not in ['Published','Hot'] and post.author == user:
        messages.success(request,"This post preview just for you nobody else can see that until this is published.")
    elif post.status in ['Published','Hot']:
        pass
    else:
        raise Http404('No post found.')
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps({'success':False,'msg':'You are not logged in.'}))
        
        referer_url = request.META['HTTP_REFERER']
        liked = request.POST.get('liked',False)
        disliked = request.POST.get('disliked',False)
        report_content = request.POST.get('report_content',None)
        if liked:
            post.like.add(request.user)
            return HttpResponse(json.dumps({'success':True,'status':'liked'}))
        elif disliked:
            post.like.remove(request.user)
            post.dislike.add(request.user)
            return HttpResponse(json.dumps({'success':True,'status':'disliked'}))
        
        if report_content and len(report_content) >= 6:
            if request.user != post.author:
                ReportContent.objects.create(type='Post',content_type=ContentType.objects.get_for_model(Post),content_id=post.pk,report_by=request.user,report_content=report_content)
                messages.success(request,"Your report has been sent to admin. and you will get notified when the issue will be solved.")
                return redirect(f"{referer_url}#feadback")
            else:
                messages.success(request,"Why you should report your own post?")
                return redirect(f"{referer_url}#feadback")
        
        messages.success(request,"Seems invalid post request.")
        return redirect(f"{referer_url}#feadback")

    else:
        page_number = int(request.GET.get('comment_page',1))
        comments = Comment.objects.filter(post=post,is_deleted=False,level=0,status="Published").order_by('-date')
        comment_paginator = Paginator(comments,10,2)
        comment_page = comment_paginator.get_page(page_number)
        return render(request,"_Blog/client/read_post.html",{'post':post,'comment_page':comment_page,})
   
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
                    if user:
                        new_comment = Comment.objects.create(post=post,parent=comment,commenter=user,content=comment_content,status="Published")
                        messages.success(request,"Your reply have been added successfully.")
                        return redirect(f"{referer_url}#comment-{new_comment.hash_id.hex}")
                    else:
                        messages.success(request,"You can't reply without sign in to your account.")
                        return redirect(f"{referer_url}#feadback")

            else:
                if user:
                    new_comment = Comment.objects.create(post=post,commenter=user,content=comment_content,status="Published")
                    messages.success(request,"Your comment have been added successfully.")
                    post_url = reverse('Blog:read_post',args=[post.category.slug,post.slug])
                    return redirect(f"{post_url}#comment-{new_comment.hash_id.hex}")
                else:
                    new_comment = Comment.objects.create(post=post,commenter=user,content=comment_content,status="Pending")
                    messages.success(request,"You are logged in to any account. Therefore, your comment under review.")
                    return redirect(f"{referer_url}#feadback")
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
    
#User profile & follow mute function
def user_profile(request,username):
    try:
        author_user = AuthorUser.objects.get(username=username)
    except:
        raise Http404
    if request.method == 'POST' and request.user != author_user:
        follow = request.POST.get('follow',None)
        mute = request.POST.get('mute',None)

        if follow:
            if request.user not in author_user.follower.all():
                author_user.follower.add(request.user)
                messages.success(request,"You are now following the user & will recieve notification about the user future post.")
                return redirect(referel_url(request))
            else:
                author_user.follower.remove(request.user)
                messages.success(request,"You are now unfollowing the user.")
                return redirect(referel_url(request))
        elif mute:
            if author_user not in request.user.mute_list.all():
                request.user.mute_list.add(author_user)
                messages.success(request,"You will not longer recieve notification of any update from the user.")
                return redirect(referel_url(request))
            else:
                request.user.mute_list.remove(author_user)
                messages.success(request,"You will be again notified about new post from the user.")
                return redirect(referel_url(request))

    else:
        page = request.GET.get('post-page',1)
        posts = author_user.live_post()
        posts_page = Paginator(posts,20)
        current_page = posts_page.get_page(page)
        list_page = current_page.paginator.get_elided_page_range(number=current_page.number,on_each_side=2,on_ends=1)
        return render(request,"_Blog/client/profile_page.html",{'author_user':author_user,'page':current_page,'list_page':list_page})

#Login a user with username or email
def signin(request):
    if request.method == "POST":
        next = request.GET.get('next',None) if request.GET.get('next',None) else reverse('Blog:signin')
        print(next)
        print(request.GET.get('next',None))
        username = extract_unique_email(request.POST.get('username',''))
        password = request.POST.get('password',None)

        user = authenticate(request=request,username=username,password=password)
        if user and user.is_active:
            login(request,user)
            return redirect(next)
        elif user and not user.is_active:
            if send_email_verify(request,user):
                messages.error(request, "The account is not activated yet. A new email has been sent with verification link.")
                return render(request,"_Blog/client/signin.html")
            else:
                messages.error(request, "Something went wrong. Please contact admin.")
                return render(request,"_Blog/client/signin.html")
        else:
            messages.error(request, "Wrong credentials, please try again with correct data.")
            return render(request,"_Blog/client/signin.html")

    else:
        if request.user.is_authenticated:
            return redirect(reverse('Blog:dashboard'))
        else:
            return render(request,"_Blog/client/signin.html")
        
#Restration for a new user
def signup(request):
    if request.user.is_authenticated:
        return redirect(reverse('Blog:dashboard'))

    if request.method == "POST":
        username = request.POST.get('username','')
        email = request.POST.get('email','')
        password1 = request.POST.get('password','')
        password2 = request.POST.get('confirm-password','')
        problem = 0
        print(email)
        try:
            if AuthorUser.objects.filter(username=username).first():
                messages.error(request,"User already exit with the username.")
                problem += 1
            elif not is_valid_username(username):
                messages.error(request,"The username is not valid!")
                problem += 1
            elif AuthorUser.objects.filter(email=extract_unique_email(email)).first():
                messages.error(request,"The email already associated with a account.")
                problem += 1
            elif BlogSetting.objects.filter(setting='forbidden-username').first():
                if username in BlogSetting.objects.filter(setting='forbidden-username').first().value.split(','):
                    messages.error(request,"The username you choosen is forbidden.")
                    problem += 1

            if password1 != password2:
                messages.error(request,"Both of the password have to be same.")
                problem += 1
            elif not is_valid_strong_password(password1):
                messages.error(request,"Please choose a bit more strong password.")
                problem += 1
        except:
            print('inside the exception scope')
            messages.error(request,"Something went wrong internally. Please contact admin.")
            problem += 1

        if not problem:
            user = AuthorUser(username=username,email=email,password=make_password(password1),is_active=False)
            
            user.save()
            print("*"*20)
            print(user.email)
            if send_email_verify(request,user):
                messages.success(request,f"Please check your email & verify the account to be finished. If you didn't received the email. Please login to the account to resend verification email.")
                return render(request,"_Blog/client/signup.html")
            else:
                message.error(request,"Something went wrong. Please contact admin.")
                return render(request,"_Blog/client/signup.html")

        else:
            return render(request,"_Blog/client/signup.html")
    else:
        return render(request,"_Blog/client/signup.html")

#Logout the logged in user
def signout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(reverse("Blog:signin"))
    else:
        return redirect(reverse("Blog:signin"))

#Verify email of new user
def email_verify(request,token):
    if verify_token(token):
        try:
            decoded_token = base64.urlsafe_b64decode(token[::-1]).decode()
            user_hash = decoded_token.split('_')[0]
            user = AuthorUser.objects.get(hash_id=user_hash[::-1])
        except:
            messages.error(request,"Something went wrong! Please contact admin.")
            return redirect(reverse('Blog:signup'))
        user.is_active = True
        user.save()
        login(request,user,backend='base.customAuthentication.CustomModelBackend')
        messages.success(request,"Your account is successfully verified.")
        return redirect(reverse('Blog:edit_profile'))
    else:
        messages.error(request,"The verificatin token is not valid or expired.")
        return redirect(reverse('Blog:signup'))