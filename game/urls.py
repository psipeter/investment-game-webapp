from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('game/', views.startGame, name='game'),
    path('information', views.information, name='information'),
    path('consent', views.consent, name='consent'),
    path('survey', views.survey, name='survey'),
    path('tutorial', views.tutorial, name="tutorial"),
    path('cash', views.cash, name="cash"),
    path('feedback', views.feedback, name="feedback"),
    path('api/status/', api_views.status),
    path('api/startGame/', api_views.startGame),
    path('api/updateGame/', api_views.updateGame),
]
