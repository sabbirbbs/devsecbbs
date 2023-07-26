#import modules
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models 


#Models Admin
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id','content','is_deleted']
    search_fields = ['content']
    # def get_queryset(self, request):
    #     # Use the default manager to show all instances, including those where is_deleted is True,
    #     # in the Django admin panel
    #     return super().get_queryset(request)

class PostAdmin(admin.ModelAdmin):
    list_display = ['title','status','date','note']
    search_fields = ['hash_id','status']

#configuring django admin

admin.site.register(models.Post,PostAdmin)
admin.site.register(models.Category)
admin.site.register(models.Comment,CommentAdmin)
admin.site.register(models.Notification)
admin.site.register(models.ReportContent)
admin.site.register(models.UserRequest)
admin.site.register(models.Series)


#Set up custom user table
fields = list(UserAdmin.fieldsets)
fields.append(('Author Info',{'fields':('profile_photo','bio','rank','gender','dob','country','city','phone')}))
fields.append(('Social Media',{'fields':('facebook_profile','twitter_profile','github_profile','website_url')}))
fields.append(('Access',{'fields':('series','follower','mute_list')}))
fields.append(('Note',{'fields':('note',)}))
UserAdmin.fieldsets = tuple(fields)

admin.site.register(models.AuthorUser,UserAdmin)
