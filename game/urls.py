from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('game/', views.startGame, name='game'),
    path('tutorial', views.startTutorial, name="tutorial"),
    path('tutorial2', views.startTutorial2, name="tutorial2"),
    path('information', views.information, name='information'),
    path('consent', views.consent, name='consent'),
    path('survey', views.survey, name='survey'),
    path('exit_survey', views.exit_survey, name='exit_survey'),
    path('cash', views.cash, name="cash"),
    path('feedback', views.feedback, name="feedback"),
    path('api/status/', api_views.status),
    path('api/startGame/', api_views.startGame),
    path('api/updateGame/', api_views.updateGame),
    path('api/startTutorial/', api_views.startTutorial),
    path('api/updateTutorial/', api_views.updateTutorial),
    path('api/restartTutorial/', api_views.restartTutorial),
    path('api/finishTutorial/', api_views.finishTutorial),
]
