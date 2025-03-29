from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),  # Required for uploads
    path('', include('recipes.urls')),
]

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

handler404 = 'recipes.views.custom_404'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

