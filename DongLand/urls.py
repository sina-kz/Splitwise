from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main_page, name="main_page"),
    path('login/', views.login_view, name="login_page"),
    path('register/', views.register_view, name="register_page"),
    path('dashboard/', views.dashboard, name="dashboard_page"),
    path('add-group/', views.add_group, name="add_group"),
    path('groups-list/', views.groups_list, name="groups_list"),
    path('friends-list/', views.friends_list, name="friends_list"),
    path('logout/', views.logout_view, name="logout_url"),
    path('add-friend/', views.add_friend, name="add_friend"),
    path('add-group-users/<group_name>/', views.add_users, name='add_users'),
    path('groups/<group_name>/', views.group_details, name='group_details'),
    path('delete-group/<token>/', views.remove_group, name='remove_group'),
    path('select-pay-method/<token>/', views.select_pay_method, name='select_pay_method'),
    path('add-expense/<token>/<type_of_calculate>/', views.add_expense, name='add_expense'),
    path('invite-user', views.invite_view, name='invite_user'),
    path('financial-report/', views.financial_report, name='financial_report')
]
