from .models import Banner, ContactInfo
def site_settings(request):
    return {"banners": Banner.objects.filter(enabled=True)[:3], "contact_info": ContactInfo.objects.first()}
