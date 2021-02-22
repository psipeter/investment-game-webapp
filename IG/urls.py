from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from game import views


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('game/', include('game.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', views.login, name="login"),
    path('accounts/logout/', views.logout, name="logout"),
    path('accounts/reset/', views.reset, name="reset"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
