from django.contrib import admin
from .models import Message
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display=("subject","from_user","to_user","created_at","is_read")
    search_fields=("subject","body")
    list_filter=("is_read","created_at")
