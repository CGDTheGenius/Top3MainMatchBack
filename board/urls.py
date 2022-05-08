from django.urls import path

from board import views

urlpatterns = [
    path('view/', views.BoardView.as_view()),

    path('cells/', views.CellList.as_view()),
    path('cells/<int:x>/<int:y>', views.CellDetail.as_view()),
    path('walls/<str:type>/<int:x>/<int:y>', views.WallDetail.as_view()),
    path('items/<int:x>/<int:y>', views.ItemList.as_view()),

    path('players/', views.PlayerList.as_view()),
    path('players/detail', views.PlayerDetail.as_view()),
    path('players/sight', views.PlayerSight.as_view()),

    path('assistants/', views.AssistantList.as_view()),
    path('assistants/detail', views.AssistantDetail.as_view()),

    path('tasks/', views.TaskList.as_view()),
    path('tasks/register', views.RegisterTask.as_view()),
    path('tasks/process/player', views.ProcessPlayerTask.as_view()),
    path('tasks/process/assistant', views.ProcessAssistantTask.as_view()),
]
