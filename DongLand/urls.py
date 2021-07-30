from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main_page, name="main_page"),
    path('login/', views.login_view, name="login_page"),
    path('register/', views.register_view, name="register_page"),
    path('dashboard/', views.dashboard, name="dashboard_page"),
    path('administrator/', views.dashboard, name="admin_page"),
    path('add-group/', views.add_group, name="add_group"),
    path('groups-list/', views.groups_list, name="groups_list"),
    path('delete-groups/', views.delete_groups, name="delete_groups"),
    path('friends-list/', views.friends_list, name="friends_list"),
    path('logout/', views.logout_view, name="logout_url")

]
