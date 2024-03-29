from django.contrib import admin
from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('', views.main_page, name="main_page"),
    path('login/', views.login_view, name="login_page"),
    path('register/', views.register_view, name="register_page"),
    path('dashboard/', views.dashboard, name="dashboard_page"),
    path('add-group/', views.add_group, name="add_group"),
    path('groups-list/', views.groups_list, name="groups_list"),
    path('admin-groups-list/', views.groups_list_admin, name="admin-groups-list"),
    path('friends-list/', views.friends_list, name="friends_list"),
    path('logout/', views.logout_view, name="logout_url"),
    path('add-friend/', views.add_friend, name="add_friend"),
    path('add-group-users/<group_name>/', views.add_users, name='add_users'),
    path('groups/<group_name>/', views.group_details, name='group_details'),
    path('delete-group/<token>/', views.remove_group, name='remove_group'),
    path('groups-admin/<group_name>/', views.group_details_admin, name='group_details_admin'),
    path('delete-group-admin/<token>/', views.remove_group_admin, name='remove_group_admin'),
    path('select-pay-method/<token>/', views.select_pay_method, name='select_pay_method'),
    path('add-expense/<token>/<type_of_calculate>/', views.add_expense, name='add_expense'),
    path('groups/<group_token>/<expense_token>/', views.expense_detail, name='expense_detail'),
    path('invite-user/', views.invite_view, name='invite_user'),
    path('remove-user/<token>/<username>/', views.remove_user, name='remove_user'),
    path('financial-report/', views.financial_report, name='financial_report'),
    path('remove-friend/<username>/', views.remove_friend, name='remove_friend'),
    path('show-users-admin/', views.show_users_admin, name='show_users_admin'),
    path('remove-user-admin/<username>/', views.remove_user_admin, name='remove_user_admin'),
    path('user-profile-admin/<username>/', views.user_profile_admin, name='user_profile_admin'),
    path('edit-expense/<group_token>/<expense_token>/<type_of_calculate>/', views.edit_expense, name='edit_expense'),
    path('view-profile/', views.user_profile, name='user_profile'),
    path('delete-user/', views.delete_user, name='delete_user'),
    path('delete-expense/<group_token>/<expense_token>/', views.delete_expense, name='delete_expense'),
    path('change-password/', views.change_password, name='change_password'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]
