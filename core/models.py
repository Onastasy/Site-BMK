from django.db import models

class Banner(models.Model):
    text = models.CharField(max_length=255)
    href = models.CharField(max_length=255, default="/")
    enabled = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    class Meta:
        ordering = ["order", "id"]
    def __str__(self): return self.text

class ContactInfo(models.Model):
    org = models.CharField(max_length=255, default="Demo Org")
    phone = models.CharField(max_length=64, default="+7 (000) 000-00-00")
    email = models.EmailField(default="info@example.com")
    address = models.CharField(max_length=255, default="Россия, Москва, ул. Пример, 1")
    def __str__(self): return self.org
