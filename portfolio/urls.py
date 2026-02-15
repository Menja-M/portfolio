from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.main.urls')),
    path('chat/', include('apps.chat.urls')),
    path(f'{settings.MEDIA_URL.lstrip("/")}/<path:path>', views.serve_media, name='serve_media'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL.lstrip('/'), document_root=settings.MEDIA_ROOT)
