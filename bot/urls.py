from django.urls import path
from .views import MainView, TaskHandler

urlpatterns = [
    path('', MainView.as_view()),
    path('<int:user_id>/<str:url_id>', TaskHandler.as_view())
]