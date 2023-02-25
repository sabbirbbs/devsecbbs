from django.urls import path
from django.conf.urls.static import static
from . import views
from base import settings

app_name = "Blog"
urlpatterns = [
    path("",views.index,name="blog_index"),
    path("dashboard",views.dashboard,name="dashboard"),
    path("write_post",views.write_post,name="write_post"),
    path("post_data/<int:pk>",views.fetch_post,name="fetch_post"),
    path("category/<str:slug>",views.category,name="category"),
    path("tag/<str:slug>",views.tag,name="tag"),
    path("post/edit/<int:id>",views.edit_post,name="edit_post"),
    path("post/<str:cat>/<str:slug>",views.view_post,name="read_post"),
    path("notifications",views.notifications,name="notifications"),
    path("comment/<int:pid>/<int:cid>",views.comment,name="comment"),
    path("test",views.test,name="test"),
    
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)