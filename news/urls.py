from django.urls import path
from . import views
app_name = "news"
urlpatterns = [
    path("", views.news_list, name="list"),
    path("create/", views.news_create, name="create"),
]
