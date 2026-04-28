from django.urls import path
from . import views
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("employees/", views.employee_list, name="employee_list"),
    path("edit/", views.edit_profile, name="edit_profile"),
    path("files/", views.user_files, name="user_files"),
]
