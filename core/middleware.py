from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class Redirect404Middleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return HttpResponseRedirect(f"{reverse('page_404')}?from={request.get_full_path()}")
        return None
