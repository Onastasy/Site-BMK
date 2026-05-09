from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views
from admin_panel import views as admin_panel_views

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
  path('privacy/', core_views.privacy_policy, name='privacy'),
  path('admin-panel/', admin_panel_views.dashboard, name='admin_dashboard'),
  path('admin-panel/users/', admin_panel_views.users_list, name='admin_users'),
  path('admin-panel/users/<int:user_id>/edit/', admin_panel_views.user_edit, name='admin_user_edit'),
  path('admin-panel/groups/', admin_panel_views.groups_list, name='admin_groups'),
  path('admin-panel/news/', admin_panel_views.news_management, name='admin_news'),
  path('admin-panel/settings/', admin_panel_views.site_settings, name='admin_settings'),
  path('admin-panel/activity/', admin_panel_views.activity_log, name='admin_activity'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

handler404 = "core.views.handler404"
