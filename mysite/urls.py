from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # namespace are unique across the entire project , 
    # can be used later to refer to blog urls
    # for eg, blog:post_list or blog:post_detail
    path('blog/', include('blog.urls', namespace='blog')),
]
