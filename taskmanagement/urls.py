from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('user/', views.user, name='user'),
    path('admin/', views.admin, name='admin'),
    path('admin-login/', views.adminlogin, name='adminlogin'),
    path('admin-logout/', views.adminlogout, name='adminlogout'),
    path('edit-task/<int:task_id>/', views.edittask, name='edit_task'),
    path('delete-task/<int:task_id>/', views.deletetask, name='delete_task'),
    path('update-task-status/<int:task_id>/', views.updatetaskstatus, name='update_status'),
    path('complete-task/<int:task_id>/', views.completetask, name='complete_task'),
]
