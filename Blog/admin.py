#import modules
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models 

#Additional function
def generate_search_fields(model):
    search_fields = []
    for field in model._meta.get_fields():
        if not field.is_relation:
            search_fields.append(field.name)
    return search_fields


#Models Admin
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id','content','is_deleted']
    search_fields = generate_search_fields(models.Comment)

class PostAdmin(admin.ModelAdmin):
    list_display = ['title','status','date','note']
    search_fields = generate_search_fields(models.Post)

class ReportContentAdmin(admin.ModelAdmin):
    list_display = ['type','report_by','status','report_content']
    search_fields = generate_search_fields(models.ReportContent)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = generate_search_fields(models.Category)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['content','note']
    search_fields = generate_search_fields(models.Notification)


class UserRequestAdmin(admin.ModelAdmin):
    list_display = ['title','content']
    search_fields = generate_search_fields(models.UserRequest)

class SeriesAdmin(admin.ModelAdmin):
    list_display = ['name','created_by']
    search_fields = generate_search_fields(models.Series)

class BlogSettingAdmin(admin.ModelAdmin):
    list_display = ['setting']
    search_fields = generate_search_fields(models.BlogSetting)

class UserLoginLogAdmin(admin.ModelAdmin):
    list_display = ['user','ip_address','user_agent','was_logged']
    search_fields = generate_search_fields(models.UserLoginLog)

class UploadedImagesAdmin(admin.ModelAdmin):
    list_display = ['user','image_url']
    search_fields = generate_search_fields(models.UploadedImages)

#configuring django admin

admin.site.register(models.Post,PostAdmin)
admin.site.register(models.Category,CategoryAdmin)
admin.site.register(models.Comment,CommentAdmin)
admin.site.register(models.Notification,NotificationAdmin)
admin.site.register(models.ReportContent,ReportContentAdmin)
admin.site.register(models.UserRequest,UserRequestAdmin)
admin.site.register(models.Series,SeriesAdmin)
admin.site.register(models.BlogSetting,BlogSettingAdmin)
admin.site.register(models.UserLoginLog,UserLoginLogAdmin)
admin.site.register(models.UploadedImages,UploadedImagesAdmin)


#Set up custom user table
fields = list(UserAdmin.fieldsets)
fields.append(('Author Info',{'fields':('profile_photo','bio','rank','gender','dob','country','city','phone_number')}))
fields.append(('Social Media',{'fields':('facebook_profile','twitter_profile','github_profile','website_url')}))
fields.append(('Access',{'fields':('series','follower','mute_list')}))
fields.append(('Note',{'fields':('note',)}))
UserAdmin.fieldsets = tuple(fields)

admin.site.register(models.AuthorUser,UserAdmin)
