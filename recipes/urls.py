from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('', views.index, name='index'),
    path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('add_ingredient/', views.add_ingredient, name='add_ingredient'),
    path('toggle_favorite/<int:recipe_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites, name='favorites'),
    path('test-404/', views.test_404, name='test_404'),

]
from django.shortcuts import render
def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

handler404 = 'recipes.views.custom_404'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
