from django.urls import path
from django.conf.urls.static import static
from . import views
from base import settings

app_name = "Blog"
urlpatterns = [
    path("",views.index,name="blog_index"),
    path("post_data/<str:hash_id>",views.fetch_post,name="fetch_post"),
    path("category/<str:slug>",views.category,name="category"),
    path("tag/<str:slug>",views.tag,name="tag"),
    path("post/<str:cat>/<str:slug>",views.view_post,name="read_post"),
    path("comment/<str:phash>/<str:chash>",views.comment,name="comment"),
    path("test",views.test,name="test"),
    #Dashboard
    path("dashboard",views.dashboard,name="dashboard"),
    path("dashboard/post/edit/<int:id>",views.edit_post,name="edit_post"),
    path("dashboard/write_post",views.write_post,name="write_post"),
    path("dashboard/post/list",views.list_post,name="list_post"),
    path("dashboard/notifications",views.notifications,name="notifications"),
    path("dashboard/notification/<str:hash_id>",views.notification_link,name="notification_link"),
    path("dashboard/reports",views.reports,name="reports"),
    path("dashboard/report/<str:hash_id>",views.report_link,name="report_link"),
    
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)