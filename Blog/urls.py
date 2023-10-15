from django.urls import path
from django.conf.urls.static import static
from Blog.views import client, dashboard
from base import settings

app_name = "Blog"
urlpatterns = [
    path("",client.index,name="blog_index"),
    path("post_data/<str:hash_id>",client.fetch_post,name="fetch_post"),
    path("category/<str:slug>",client.category,name="category"),
    path("series/<str:slug>",client.series,name="series"),
    path("tag/<str:slug>",client.tag,name="tag"),
    path("post/<str:cat>/<str:slug>",client.view_post,name="read_post"),
    path("comment/<str:phash>/<str:chash>",client.comment,name="comment"),
    path("user/<str:username>",client.user_profile,name='user_profile'),
    path("signin",client.signin,name="signin"),
    path("signup",client.signup,name="signup"),
    path("signout",client.signout,name="signout"),
    path("verify/<str:token>",client.email_verify,name="email_verify"),
    path("reset/<str:token>",client.password_reset,name="password_reset"),
    path("about-us",client.about_us,name="about_us"),
    path("contact-us",client.contact_us,name="contact_us"),
    path("tos",client.tos,name="tos"),
    path("privacy",client.privacy,name="privacy"),
    
    #Dashboard
    path("dashboard",dashboard.dashboard,name="dashboard"),
    path("dashboard/view_profile",dashboard.view_profile,name="view_profile"),
    path("dashboard/edit_profile",dashboard.edit_profile,name="edit_profile"),
    path("dashboard/change_password",dashboard.change_password,name="change_password"),
    path("dashboard/post/edit/<str:hash_id>",dashboard.edit_post,name="edit_post"),
    path("dashboard/write_post",dashboard.write_post,name="write_post"),
    path("dashboard/post/list",dashboard.list_post,name="list_post"),
    path("dashboard/notifications",dashboard.notifications,name="notifications"),
    path("dashboard/notification/<str:hash_id>",dashboard.notification_link,name="notification_link"),
    path("dashboard/reports",dashboard.reports,name="reports"),
    path("dashboard/report/<str:hash_id>",dashboard.report_link,name="report_link"),
    path("dashboard/pending",dashboard.pending_post,name='pending_post'),
    path("dashboard/pending_comment",dashboard.pending_comment,name='pending_comment'),
    path("dashboard/pending_request",dashboard.pending_request,name='pending_request'),
    path("dashboard/upload-image",dashboard.upload_image,name="image-upload"),
    path("dashboard/suneditor_gallery",dashboard.suneditor_gallery,name="suneditor_gallery"),
    path("dashboard/send_request",dashboard.save_request,name="send_request"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)