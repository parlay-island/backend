"""
urls.py

Authors: Jake Derry, Holly Ansel

Contains the url paths of the entire project. It may be helpful to break
this into a separate url file for the teacher urls like `teacher.urls`.

Contains authentication endpoints that are offered through djoser which is
an extension of django REST framework.
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

import teacher.views
import teacher.health

urlpatterns = [
    path('', teacher.health.health_check),
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/', include('djoser.urls.authtoken')),
    path('admin/', admin.site.urls),
    path('questions/', teacher.views.question_view.questions_controller),
    path('questions/<int:question_id>', teacher.views.question_view.question_controller),
    path('results/summary/', teacher.views.result_view.results_controller),
    path('players/', teacher.views.player_view.players_controller),
    path('players/me/', teacher.views.player_view.me_controller),
    path('players/<int:player_id>/', teacher.views.player_view.player_controller),
    path('players/<int:player_id>/results/', teacher.views.player_view.player_results_controller),
    path('teachers/me/', teacher.views.teacher_view.me_controller),
    path('levels/<int:level>/results/', teacher.views.level_views.level_results_controller),
    path('levels/', teacher.views.level_views.levels_controller),
    path('levels/<int:level_id>/', teacher.views.level_views.level_controller)
]
