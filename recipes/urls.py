from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('splash/', views.splash, name='splash'),
    path('wifi/', views.wifi_setup, name='wifi_setup'),
    path('configured/', views.configured, name='configured'),
    path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('add_ingredient/', views.add_ingredient, name='add_ingredient'),
    path('toggle_favorite/<int:recipe_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites, name='favorites'),
    path('test-404/', views.test_404, name='test_404'),
    path('shutdown/', views.shutdown, name='shutdown'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
