from .models import Banner, ContactInfo
from .breadcrumbs import get_breadcrumbs
def site_settings(request):
    return {"banners": Banner.objects.filter(enabled=True)[:3], "contact_info": ContactInfo.objects.first()}

def breadcrumbs(request):
    """Хлебные крошки для всех страниц"""
    return {'breadcrumbs': get_breadcrumbs(request)}