from django.urls import path
from . import views

urlpatterns = [
    path('game/', views.startGame, name='game'),
    path('information', views.information, name='information'),
    path('consent', views.consent, name='consent'),
    path('survey', views.survey, name='survey'),
    path('tutorial', views.tutorial, name="tutorial"),
    path('updateGame', views.updateGame, name="updateGame"),
    path('stats', views.stats, name="stats"),
    path('cash', views.cash, name="cash"),
    path('feedback', views.feedback, name="feedback"),
]