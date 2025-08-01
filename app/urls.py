from django.urls import path
from .views import register_view,login_view,logout_view,todo_view,mark_done,delete_task,activate_account,activation_email

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('todo/', todo_view, name='todo'),
    path('done/<int:task_id>/', mark_done, name='mark_done'),
    path('delete/<int:task_id>/', delete_task, name='delete_task'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    path('activate-email/', activation_email, name='activation_email'),
]
