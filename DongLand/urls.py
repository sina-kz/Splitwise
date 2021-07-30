from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main_page, name="main_page"),
    path('login/', views.login_view, name="login_page"),
    path('register/', views.register_view, name="register_page"),
    path('dashboard/', views.dashboard, name="dashboard_page"),
    path('administrator/', views.dashboard, name="admin_page"),
    path('add_group/', views.add_group, name="add_group"),
    path('logout/', views.logout_view, name="logout_url")

]
