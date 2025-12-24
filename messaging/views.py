from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Message
from .forms import SendMessageForm

@login_required
def inbox(request):
    return render(request, "messaging/inbox.html", {
        "inbox_items": Message.objects.filter(to_user=request.user)[:50],
        "outbox_items": Message.objects.filter(from_user=request.user)[:50],
        "form": SendMessageForm(),
    })

@login_required
def send_message(request):
    if request.method != "POST":
        return redirect("messaging:inbox")
    form = SendMessageForm(request.POST)
    if form.is_valid():
        to_user = User.objects.get(username=form.cleaned_data["to_username"])
        Message.objects.create(
            from_user=request.user,
            to_user=to_user,
            subject=form.cleaned_data["subject"],
            body=form.cleaned_data["body"],
        )
        return redirect("messaging:inbox")
    return render(request, "messaging/inbox.html", {
        "inbox_items": Message.objects.filter(to_user=request.user)[:50],
        "outbox_items": Message.objects.filter(from_user=request.user)[:50],
        "form": form,
    })
