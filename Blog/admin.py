#import modules
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models 


#configuring django admin

admin.site.register(models.Post)
admin.site.register(models.Category)
admin.site.register(models.Comment)
admin.site.register(models.Notification)


#Set up custom user table
fields = list(UserAdmin.fieldsets)
fields.append(('Author Info',{'fields':('profile_photo','bio','rank','dob','country','city','phone')}))
UserAdmin.fieldsets = tuple(fields)

admin.site.register(models.AuthorUser,UserAdmin)
