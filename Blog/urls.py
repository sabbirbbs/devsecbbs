from django.urls import path
from django.conf.urls.static import static
from . import views
from base import settings

app_name = "Blog"
urlpatterns = [
    path("",views.index,name="blog_index"),
    path("post_data/<str:hash_id>",views.fetch_post,name="fetch_post"),
    path("category/<str:slug>",views.category,name="category"),
    path("series/<str:slug>",views.series,name="series"),
    path("tag/<str:slug>",views.tag,name="tag"),
    path("post/<str:cat>/<str:slug>",views.view_post,name="read_post"),
    path("comment/<str:phash>/<str:chash>",views.comment,name="comment"),
    path("user/<str:username>",views.user_profile,name='user_profile'),
    path("signin",views.signin,name="signin"),
    path("signup",views.signup,name="signup"),
    path("signout",views.signout,name="signout"),
    path("verify/<str:token>",views.email_verify,name="email-verify"),
    #Dashboard
    path("dashboard",views.dashboard,name="dashboard"),
    path("dashboard/view_profile",views.view_profile,name="view_profile"),
    path("dashboard/edit_profile",views.edit_profile,name="edit_profile"),
    path("dashboard/post/edit/<str:hash_id>",views.edit_post,name="edit_post"),
    path("dashboard/write_post",views.write_post,name="write_post"),
    path("dashboard/post/list",views.list_post,name="list_post"),
    path("dashboard/notifications",views.notifications,name="notifications"),
    path("dashboard/notification/<str:hash_id>",views.notification_link,name="notification_link"),
    path("dashboard/reports",views.reports,name="reports"),
    path("dashboard/report/<str:hash_id>",views.report_link,name="report_link"),
    path("dashboard/pending",views.pending_post,name='pending_post'),
    path("dashboard/pending_comment",views.pending_comment,name='pending_comment'),
    path("dashboard/pending_request",views.pending_request,name='pending_request'),
    
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)