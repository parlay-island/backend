"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import teacher.views
import teacher.health
import teacher.views.player_view

urlpatterns = [
    path('', teacher.health.health_check),
    path('admin/', admin.site.urls),
    path('questions/', teacher.views.question_view.questions_controller),
    path('questions/<int:questionId>', teacher.views.question_view.question_controller),
    path('results/summary/', teacher.views.result_view.results_controller),
    path('players/<int:playerId>/results/', teacher.views.player_view.player_results_controller),
    path('levels/<int:level>/results/', teacher.views.level_views.level_results_controller),
    path('levels/', teacher.views.level_views.levels_controller),
    path('levels/<int:level_id>/', teacher.views.level_views.level_controller)
]
