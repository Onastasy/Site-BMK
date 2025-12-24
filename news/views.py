from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect
from .models import NewsPost
from .forms import NewsPostForm

def news_list(request):
    return render(request, "news/list.html", {"posts": NewsPost.objects.all()[:50]})

@permission_required("news.add_newspost", raise_exception=True)
def news_create(request):
    if request.method == "POST":
        form = NewsPostForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            return redirect("news:list")
    else:
        form = NewsPostForm()
    return render(request, "news/create.html", {"form": form})
