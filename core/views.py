from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q
from .forms import ContactForm
from news.models import NewsPost
from core.models import ContactInfo

def home(request): return render(request, "core/home.html")
def about(request): return render(request, "core/about.html")

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, "Сообщение принято (демо).")
            return render(request, "core/thanks.html", {"data": form.cleaned_data})
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})

def sitemap(request): return render(request, "core/sitemap.html")

def search(request):
    q = (request.GET.get("q") or "").strip()
    results = []
    if q:
        pages = [
            (reverse("home"), "Главная", "Главная страница сайта."),
            (reverse("about"), "О сайте", "Описание проекта и возможностей."),
            (reverse("about_us"), "О нас", "Информация о компании/проекте."),
            (reverse("advantages"), "Преимущества", "Преимущества компании/сервиса."),
            (reverse("team"), "Наша команда", "Информация о команде."),
            (reverse("vacancies"), "Вакансии", "Актуальные вакансии."),
            (reverse("news:list"), "Новости", "Лента новостей."),
            (reverse("messaging:inbox"), "Сообщения", "Система обмена сообщениями."),
            (reverse("contact"), "Контакты", "Контактная информация и форма."),
            (reverse("sitemap"), "Карта сайта", "Список разделов."),
        ]
        ql = q.lower()
        for url, title, snippet in pages:
            if ql in (title + " " + snippet).lower():
                results.append({"url": url, "title": title, "snippet": snippet})

        for n in NewsPost.objects.filter(Q(title__icontains=q) | Q(body__icontains=q)).order_by("-created_at")[:20]:
            results.append({"url": reverse("news:list"), "title": f"Новость: {n.title}", "snippet": (n.body[:140] + "...") if len(n.body)>140 else n.body})

        c = ContactInfo.objects.first()
        if c and ql in f"{c.org} {c.phone} {c.email} {c.address}".lower():
            results.append({"url": reverse("contact"), "title": "Контакты", "snippet": "Совпадение в контактной информации."})
    return render(request, "core/search.html", {"q": q, "results": results})

def page_404(request):
    return render(request, "core/404.html", {"missing": request.GET.get("from","")}, status=404)

def handler404(request, exception):
    return render(request, "core/404.html", {"missing": request.get_full_path()}, status=404)


def about_us(request):
    return render(request, "core/about_us.html")

def advantages(request):
    return render(request, "core/advantages.html")

def team(request):
    return render(request, "core/team.html")

def vacancies(request):
    return render(request, "core/vacancies.html")

def privacy_policy(request):
    """Политика конфиденциальности"""
    return render(request, "core/privacy.html")
