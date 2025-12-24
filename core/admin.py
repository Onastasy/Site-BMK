from django.contrib import admin
from .models import Banner, ContactInfo

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display=("text","href","enabled","order")
    list_editable=("enabled","order")

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display=("org","phone","email","address")
