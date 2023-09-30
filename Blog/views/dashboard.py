#import modules
from django.shortcuts import render, redirect
from django.http import HttpResponse,Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from Blog.models import *
from PIL import Image
import json
from taggit.models import Tag
import datetime
from django.db.models import Q
import os
from django.contrib import messages
from django.core.paginator import Paginator
from Blog.extrafunc import *
from Blog.token import *
import requests as rq
import base64


#User dashboard
@login_required
def dashboard(request):
    return render(request,'_Blog/dashboard/dashboard.html')

#Listing the post owned by user in dashboard
@login_required
def list_post(request):
    if request.method == "POST":
        page_number = int(request.GET.get('page',1))
        query = request.POST.get('query',None)

        if request.user.is_superuser or request.user.rank == "Admin":
            post = Post.objects.filter(Q(title__contains=query)|Q(description__contains=query)|Q(status__contains=query)|Q(slug__contains=query)|Q(category__name__contains=query))
        else:
            post = Post.objects.filter(Q(title__contains=query)|Q(description__contains=query)|Q(status__contains=query)|Q(slug__contains=query)|Q(category__name__contains=query),is_deleted=False,author=request.user)

        if post:
            page_number = int(request.GET.get('page',1))
            paginator = Paginator(post,len(post))
            page = paginator.get_page(page_number)
            list_page = page.paginator.get_elided_page_range(number=page.number,on_each_side=2,on_ends=1)
            return render(request,"_Blog/dashboard/list_post.html",{'page':page,'list_page':list_page})
        else:
            return render(request,"_Blog/dashboard/list_post.html",{'page':None,'list_page':None,'query':'Not found'})
    else:
        page_number = int(request.GET.get('page',1))
        if request.user.is_superuser or request.user.rank == "Admin":
            post = Post.objects.filter()
        else:
            post = Post.objects.filter(is_deleted=False,author=request.user)
        paginator = Paginator(post,10,3)
        page = paginator.get_page(page_number)
        list_page = page.paginator.get_elided_page_range(number=page.number,on_each_side=2,on_ends=1)
        return render(request,"_Blog/dashboard/list_post.html",{'page':page,'list_page':list_page})

#validating & saving written post
@login_required
@for_banned_user
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
            category = Category.objects.get(hash_id=request.POST.get('category',None))
        except Exception as error:
            response = {"status":"error","message":"Unable to find category you selected!"}
            return HttpResponse(json.dumps(response)) 

        try:
            series = Series.objects.get(hash_id=request.POST.get('series',None))
            if series in request.user.series.all():
                series = series
        except:
            series = None


        if 5 > len(title) > 255 :
            return HttpResponse(json.dumps({"status":"error","message":"Your post title should not be blank and more than 255 character."}))
        elif len(title) > 254:
            return HttpResponse(json.dumps({"status":"error","message":"Your post title is too long."}))
        elif cover_photo:
            try:
                Image.open(cover_photo)
            except:
                return HttpResponse(json.dumps({"status":"error","message":"Thanks for try to upload not an image or any payload."}))
        elif not cover_photo and author.rank in ['Contributor','Banned']:
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
        
        new_post = Post.objects.create(title=title,description=description,series=series,cover_photo=cover_photo,content=content,category=category,author=author,status=status)
        new_post.tags.add(*tags)
        new_post.save()
        messages.success(request,"Your post has been successfully added. Now you are in edit mode.")
        edit_post_url = root_url(request) +str(reverse('Blog:edit_post', args = [new_post.hash_id] ))
        response = {"status":"success","message":"Post has been saved successfully",'destination':edit_post_url}
        # Resize and reduce the image size
        try:
            image_path = new_post.cover_photo.path
            resize_image(image_path,output_size=(600,300))
        except:
            pass
        return HttpResponse(json.dumps(response))
    else:
        category = Category.objects.filter(level=0)
        tags = Tag.objects.all()
        return render(request,'_Blog/dashboard/write_post.html',{'category':category,'tags':tags})

#Post edit
@login_required
@for_banned_user
def edit_post(request,hash_id):

    try:
        if request.user.is_superuser or request.user.rank == "Admin":
            _post = Post.objects.get(hash_id=hash_id)
        else:
            _post = Post.objects.get(hash_id=hash_id,is_deleted=False,author=request.user)
    except:
        raise Http404


    if request.method == "POST":
        
        is_delete = request.POST.get('delete',False)
        if is_delete == 'true':
            _post.is_deleted = True
            _post.save()
            messages.success(request,f"Your post titled '{_post.title}' has been deleted.")
            return redirect(reverse('Blog:list_post'))
        
        if _post.status == 'Pending':
            return HttpResponse(json.dumps({"status":"error","message":"While your post are pending under review. You can't make any change for now. Not even by manupulate the request."}))
        elif _post.status == 'Rejected':
            return HttpResponse(json.dumps({"status":"error","message":"While your post are rejected. Please improve that for being accepted."}))

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
            category = Category.objects.get(hash_id=request.POST.get('category',None))
        except:
            response = {"status":"error","message":"Unable to find category you selected!"}
            return HttpResponse(json.dumps(response)) 

        try:
            series = Series.objects.get(hash_id=request.POST.get('series',None))
            if series in request.user.series.all():
                series = series
        except:
            series = None   

        if 5 > len(title) > 255 :
            return HttpResponse(json.dumps({"status":"error","message":"Your post title should not be blank and less than 255 character."}))
        elif cover_photo:
            try:
                Image.open(cover_photo)
            except:
                return HttpResponse(json.dumps({"status":"error","message":"Thanks for try to upload not an image or any payload."}))
        elif (not cover_photo and not _post.cover_photo) and author.rank in ['Contributor','Banned']:
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
        _post.series = series
        _post.description = description
        _post.content = content
        _post.category = category
        _post.author = author
        _post.status = status
        _post.last_modified = datetime.datetime.now()
        if cover_photo:
            print("yes. got a cover photo")
            #remove old cover photo if exits
            try:
                print('try to remove old cover photo')
                old_cover_path = _post.cover_photo.path
                os.remove(old_cover_path)
            except Exception as error:
                _post.cover_photo = cover_photo
        else:
            pass
        _post.tags.add(*tags)
        _post.save()
        # Resize and reduce the image size
        try:
            image_path = _post.cover_photo.path
            resize_image(image_path,output_size=(600,300))
        except Exception as error:
            print(error)

        if not feadback_msg:
            feadback_msg = "Your post have been successfully edited."
        response = {"status":"success","message":feadback_msg}
        return HttpResponse(json.dumps(response))
    else:
        if request.user.rank == "Admin" or request.user.is_superuser:
            is_restore = request.GET.get('restore',False)
            if is_restore == 'true':
                _post.is_deleted = False
                _post.save()
                messages.success(request,f"Your post titled '{_post.title}' has been restored.")
                return redirect(reverse('Blog:list_post'))
        
        if _post.status == 'Pending':
            messages.error(request,"While your post are pending under review. You can't make any change for now.")
            return render(request,'_Blog/dashboard/edit_post.html',{'post':_post})
        elif _post.status == 'Rejected':
            messages.error(request,"While your post are rejected. Please improve that for being accepted.")
            return render(request,'_Blog/dashboard/edit_post.html',{'post':_post})
        else:
            post = Post.objects.get(hash_id=hash_id)
            category = Category.objects.filter(level=0)
            tags = Tag.objects.all()
            if post.author == request.user or (request.user.is_superuser or request.user.rank == "Admin"):
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

#Notification page & mark as read
@login_required
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
            messages.success(request,f'Your all {read} are already marked as read.')
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
@login_required
def notification_link(request,hash_id):
    try:
        notification = Notification.objects.get(user=request.user,hash_id=hash_id)
    except:
        messages.error(request,'There are have no such notification found.')
        return redirect(reverse('Blog:notifications'))
    if notification.type == 'Comment':
        post = notification.content_object.post
        comments = Comment.objects.filter(post=post,is_deleted=False,level=0,status='Published').order_by('-date')
        page_of_comment = comment_page(comments,notification.content_object) #get the comment page
        post_url = reverse('Blog:read_post',args=[post.category.slug,post.slug])
        url_to_redirect = f"{post_url}?comment_page={page_of_comment}#comment-{notification.content_object.hash_id.hex}"
    elif notification.type == 'Like':
        post = notification.content_object
        url_to_redirect = reverse('Blog:read_post',args=[post.category.slug,post.slug])
    elif notification.type == 'Follow':
        follower = notification.content_object
        url_to_redirect = reverse('Blog:user_profile',args=[follower.username])
    elif notification.type == 'Update':
        if notification.content_type.name == 'post':
            post = notification.content_object
            url_to_redirect = reverse('Blog:read_post',args=[post.category.slug,post.slug])
        elif notification.content_type.name == 'author user':
            author = notification.content_object
            url_to_redirect = reverse('Blog:user_profile', args=[author.username])
        elif notification.content_type.name == 'report content':
            report = notification.content_object
            url_to_redirect = reverse('Blog:report_link', args=[report.hash_id.hex])
        else: 
            messages.error(request,"The notification doesn't linked with anything.")
            url_to_redirect = referel_url(request)
    elif notification.type == 'Notice':
        if notification.content_type.name == 'author user':
            author = notification.content_object
            url_to_redirect = reverse('Blog:user_profile', args=[author.username])
        elif notification.content_type.name == 'report content':
            report = notification.content_object
            url_to_redirect = reverse('Blog:report_link', args=[report.hash_id.hex])
        else:
            messages.error(request,"The notification doesn't linked with anything.")
            url_to_redirect = referel_url(request)
    else:
        pass
    notification.read_time = datetime.datetime.now() #Mark the notification as read
    notification.save()
    return redirect(url_to_redirect)

#Report pages
def get_report_page(page,type=None):
    try:
        if type:
            reports = ReportContent.objects.filter(type=type,status='Pending')
        else:
            reports = ReportContent.objects.filter(status='Pending')
        reports_page = Paginator(reports,3)
        current_page = reports_page.get_page(page)
    except:
        current_page = []

    return current_page

#Generate link of report content
@login_required
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
            comments = Comment.objects.filter(post=comment.post,is_deleted=False,level=0,status='Published').order_by('-date')
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
@login_required
@admin_mod_only
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

#Pending post
@login_required
@admin_mod_only
def pending_post(request):
    if request.method == "POST":
        post_hash_id = request.POST.get('post_hash_id',"")
        if is_valid_uuid(post_hash_id) and Post.objects.filter(hash_id=post_hash_id).exists():
            post = Post.objects.get(hash_id=post_hash_id)
            status = request.POST.get('status',None)
            reason = request.POST.get('reason',None)
            if status in ['Published','Hot','Rejected']:
                post.status = status
                if reason:
                    post.note = reason
            post.save() #Saving the post after updating status
            messages.success(request,f'The post is successfully marked as {status}.')
            return redirect(referel_url(request))
        else:
            messages.error(request,'The post that your are trying to review not found.')
            return redirect(referel_url(request))
    else:
        page = request.GET.get('page',1)
        posts = Post.objects.filter(status='Pending')
        posts_page = Paginator(posts,1)
        current_page = posts_page.get_page(page)

        context = {
            'page' : current_page,
        }
        return render(request,'_Blog/dashboard/pending_item/pending_post.html',context)

#Pending comment  
@login_required
@admin_mod_only
def pending_comment(request):
    if request.method == "POST":
        comment_hash_id = request.POST.get('comment_hash_id',"")
        if is_valid_uuid(comment_hash_id) and Comment.objects.filter(hash_id=comment_hash_id).exists():
            comment = Comment.objects.get(hash_id=comment_hash_id)
            status = request.POST.get('status',None)
            reason = request.POST.get('reason',None)
            if status in ['Published','Hot','Rejected']:
                comment.status = status
                if reason:
                    comment.note = reason
            comment.save() #Saving the comment after updating status
            messages.success(request,f'The comment is successfully marked as {status}.')
            return redirect(referel_url(request))
        else:
            messages.error(request,'The comment that your are trying to review not found.')
            return redirect(referel_url(request))
    else:
        page = request.GET.get('page',1)
        comments = Comment.objects.filter(status='Pending')
        comments_page = Paginator(comments,3)
        current_page = comments_page.get_page(page)

        context = {
            'page' : current_page,
        }
        return render(request,'_Blog/dashboard/pending_item/pending_comment.html',context)

#Pending request
@login_required
@admin_mod_only
def pending_request(request):
    if request.method == "POST":
        request_hash_id = request.POST.get('request_hash_id',"")
        if is_valid_uuid(request_hash_id) and UserRequest.objects.filter(hash_id=request_hash_id).exists():
            user_request = UserRequest.objects.get(hash_id=request_hash_id)
            status = request.POST.get('status',None)
            reason = request.POST.get('reason',None)
            if status in ['Accepted','Rejected']:
                user_request.status = status
                if reason:
                    user_request.note = reason
            user_request.review_date = datetime.datetime.now()
            user_request.save() #Saving the request after updating status
            messages.success(request,f'The request is successfully marked as {status}.')
            return redirect(referel_url(request))
        else:
            messages.error(request,'The request that your are trying to review not found.')
            return redirect(referel_url(request))
    else:
        page = request.GET.get('page',1)
        user_requests = UserRequest.objects.filter(status='Pending')
        request_page = Paginator(user_requests,3)
        current_page = request_page.get_page(page)

        context = {
            'page' : current_page,
        }
        return render(request,'_Blog/dashboard/pending_item/pending_request.html',context)

#View the user profile info in dashboard
@login_required
def view_profile(request):
    return render(request,"_Blog/dashboard/view_profile.html")
  
#Edit user profile info
@login_required
def edit_profile(request):
    if request.method == "POST":
        user_profile = request.user
        try:
            user_profile.first_name = request.POST.get('fname', user_profile.first_name)
            user_profile.last_name = request.POST.get('lname', user_profile.last_name)
            user_profile.bio = request.POST.get('bio', user_profile.bio)
            user_profile.website_url = request.POST.get('website', user_profile.website_url)
            user_profile.facebook_profile = request.POST.get('facebook', user_profile.facebook_profile)
            user_profile.twitter_profile = request.POST.get('twitter', user_profile.twitter_profile)
            user_profile.github_profile = request.POST.get('github', user_profile.github_profile)
            user_profile.phone = phone_is_valid(request.POST.get('phone', user_profile.phone))
            user_profile.country = request.POST.get('country', user_profile.country)
            user_profile.city = request.POST.get('city', user_profile.city)

            # Filter gender input
            gender = request.POST.get('gender', user_profile.gender)
            if gender in ['Male', 'Female', 'Non-Binary']:
                user_profile.gender = gender
            else:
                # If an invalid gender value is provided, use the existing value
                user_profile.gender = user_profile.gender
            
            # Filter dob input
            dob = request.POST.get('dob', user_profile.dob)
            try:
                dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
                user_profile.dob = dob_date
            except ValueError:
                # If an invalid date is provided, use the existing value
                user_profile.dob = user_profile.dob

            # Handle profile photo upload
            profile_photo = request.FILES.get('profile_photo',None)
            if profile_photo:
                try:
                    # Validate image size (less than 20 MB)
                    if profile_photo.size > 20 * 1024 * 1024:
                        messages.error(request,"Profile photo size is more than expected.")
                        return redirect(request.META['HTTP_REFERER'])
                    
                    #Check if actually this is an image
                    try:
                        Image.open(profile_photo)
                    except:
                        messages.error(request,"Thanks for try to upload not an image or any payload.")
                        return redirect(request.META['HTTP_REFERER'])
                    
                    #check allow file type if not return error
                    filename, extension = os.path.splitext(profile_photo.name)
                    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                    if extension.lower() not in allowed_extensions:
                        messages.error(request,"Please upload allowed image type.")
                        return redirect(request.META['HTTP_REFERER'])
                        
                    # Delete the old profile photo if it exists
                    if user_profile.profile_photo:
                        # Remove the old file from the file system
                        try:
                            file_path = user_profile.profile_photo.path
                            os.remove(file_path)
                        except:
                            pass

                    # Save the new profile photo
                    user_profile.profile_photo = profile_photo


                except Exception as e:
                    # Handle invalid file uploads (e.g., display an error message)
                    messages.error(request,"Something went wrong with the profile photo!")
                    return redirect(request.META['HTTP_REFERER'])

            user_profile.save()

            # Resize and reduce the image size
            try:
                image_path = user_profile.profile_photo.path
                resize_image(image_path)
            except:
                pass

        except:
            messages.error(request,"Something went wrong. Please fill the form carefully.")
            return redirect(request.META['HTTP_REFERER'])

        messages.success(request,"Your profile has been successfully updated!")
        return redirect(reverse("Blog:view_profile"))
    else:
        return render(request,"_Blog/dashboard/edit_profile.html")

#Upload image for use in wysiwyg
@login_required    
def upload_image(request):
    image = request.FILES.get('file-0',None)
    user = request.user if request.user.is_authenticated else None
    try:
        Image.open(image)
    except:
        image = None
        
    if image:
        try:
            imagebase64 = base64.b64encode(image.read()).decode()
            apiKey = BlogSetting.objects.filter(setting='imgbb-apikey').first().value
            apiUrl = 'https://api.imgbb.com/1/upload'
            try:
                response = rq.post(apiUrl,data={'key':apiKey,'image':imagebase64})
                data = json.loads(response.text)
                if data['success']:
                    uploaded_image = data['data']['image']
                    UploadedImages(user=user,image_url=uploaded_image['url']).save()
                    response = {
                            "result": [ { "url": uploaded_image['url'], "name": uploaded_image['name'], "size": data['data']['size']}, ]
                    }
            except:
                upload_image = UploadedImages(user=user,image=image)
                upload_image.save()
                response = {
                        "result": [ { "url": upload_image.image.url , "name": image.name, "size": image.size}, ]
                }
        except Exception as error:
            print(error)
            response = {'errorMessage':"Unable to upload the images"}

    return HttpResponse(json.dumps(response))

@login_required
def change_password(request):
    if request.method == 'POST':
        old_pass = request.POST.get('old-password',None)
        new_password = request.POST.get('password',None)
        confirm_password = request.POST.get('confirm-password',None)
        if request.user.check_password(old_pass):
            if new_password == confirm_password:
                if is_valid_strong_password(new_password):
                    request.user.set_password(new_password)
                    request.user.save()
                    messages.success(request,"Your password has been changed successfully.")
                    return redirect(reverse('Blog:signin'))
                else:
                    messages.error(request,"The password is not hard enongh. Please choose a secure password.")
            else:
                messages.error(request,"New password & confirm new password have to be same.")
        else:
            messages.error(request,"Sorry, your old password is not correct. Please check again.")   
    
        return render(request,"_Blog/dashboard/change_password.html")
    else:
        return render(request,"_Blog/dashboard/change_password.html")

def suneditor_gallery(request):
    if request.user.is_authenticated:
        user = request.user
        author_images = UploadedImages.objects.filter(user=user)
        public_images = UploadedImages.objects.filter(user=None)
        total_image = author_images.union(public_images)
        response = {
            "statusCode":200,
            "result" : []
        }

        for image in total_image:
            if not image.user:
                tag = "Public images"
            else:
                tag = 'Your images'

            tag = "Public images" if not image.user else 'Your images'
            url = root_url(request)+image.image.url if not image.image_url else image.image_url
            result = {
                'src' : url,
                'name' : '',
                'alt' : '',
                'tag' : tag
            }
            response['result'].append(result)


        return JsonResponse(response)

    else:
        response = {
                    "statusCode": 404,
                }
        return JsonResponse(response)