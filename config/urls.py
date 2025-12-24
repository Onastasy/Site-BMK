from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
  path("admin/", admin.site.urls),
  path("", core_views.home, name="home"),
  path("about/", core_views.about, name="about"),

  path("about-us/", core_views.about_us, name="about_us"),
  path("advantages/", core_views.advantages, name="advantages"),
  path("team/", core_views.team, name="team"),
  path("vacancies/", core_views.vacancies, name="vacancies"),
  path("contact/", core_views.contact, name="contact"),
  path("sitemap/", core_views.sitemap, name="sitemap"),
  path("search/", core_views.search, name="search"),
  path("404/", core_views.page_404, name="page_404"),
  path("news/", include("news.urls")),
  path("messages/", include("messaging.urls")),
  path("accounts/", include("accounts.urls")),
]

handler404 = "core.views.handler404"
