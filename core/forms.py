from django import forms
class ContactForm(forms.Form):
    name = forms.CharField(label="Имя", max_length=100)
    message = forms.CharField(label="Сообщение", widget=forms.Textarea(attrs={"rows":5}))
