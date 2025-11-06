from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from chatroom.chat import views as chat_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chatroom.chat.urls'))
]

if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve GridFS-backed media at /mediafs/<id>/ (works in production too)
urlpatterns += [
    path('mediafs/<str:file_id>/', chat_views.mediafs_view, name='mediafs')
]
