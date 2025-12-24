from django import forms
from django.contrib.auth.models import User

class SendMessageForm(forms.Form):
    to_username = forms.CharField(label="Кому (логин)", max_length=150)
    subject = forms.CharField(label="Тема", max_length=200)
    body = forms.CharField(label="Текст", widget=forms.Textarea(attrs={"rows":4}))

    def clean_to_username(self):
        u = self.cleaned_data["to_username"].strip()
        if not User.objects.filter(username=u).exists():
            raise forms.ValidationError("Нет такого пользователя.")
        return u
