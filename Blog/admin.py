#import modules
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models 


#Models Admin
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id','content','is_deleted']
    search_fields = [field.name for field in models.Comment._meta.fields]

class PostAdmin(admin.ModelAdmin):
    list_display = ['title','status','date','note']
    search_fields = [field.name for field in models.Post._meta.fields]

class ReportContentAdmin(admin.ModelAdmin):
    list_display = ['report_type','report_by','status','report_content']
    search_fields = [field.name for field in models.ReportContent._meta.fields]

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = [field.name for field in models.ReportContent._meta.fields]

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['content','note']
    search_fields = [field.name for field in models.ReportContent._meta.fields]


class UserRequestAdmin(admin.ModelAdmin):
    list_display = ['title','content']
    search_fields = [field.name for field in models.ReportContent._meta.fields]

class SeriesAdmin(admin.ModelAdmin):
    list_display = ['name','created_by']
    search_fields = [field.name for field in models.ReportContent._meta.fields]

#configuring django admin

admin.site.register(models.Post,PostAdmin)
admin.site.register(models.Category,CategoryAdmin)
admin.site.register(models.Comment,CommentAdmin)
admin.site.register(models.Notification,NotificationAdmin)
admin.site.register(models.ReportContent,ReportContentAdmin)
admin.site.register(models.UserRequest,UserRequestAdmin)
admin.site.register(models.Series,SeriesAdmin)


#Set up custom user table
fields = list(UserAdmin.fieldsets)
fields.append(('Author Info',{'fields':('profile_photo','bio','rank','gender','dob','country','city','phone')}))
fields.append(('Social Media',{'fields':('facebook_profile','twitter_profile','github_profile','website_url')}))
fields.append(('Access',{'fields':('series','follower','mute_list')}))
fields.append(('Note',{'fields':('note',)}))
UserAdmin.fieldsets = tuple(fields)

admin.site.register(models.AuthorUser,UserAdmin)
