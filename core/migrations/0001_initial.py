# Generated for coursework demo (pre-created migrations to avoid makemigrations step)
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name="Banner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.CharField(max_length=255)),
                ("href", models.CharField(default="/", max_length=255)),
                ("enabled", models.BooleanField(default=True)),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "ordering": ["order", "id"],
            },
        ),
        migrations.CreateModel(
            name="ContactInfo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("org", models.CharField(default="Demo Org", max_length=255)),
                ("phone", models.CharField(default="+7 (000) 000-00-00", max_length=64)),
                ("email", models.EmailField(default="info@example.com", max_length=254)),
                ("address", models.CharField(default="Россия, Москва, ул. Пример, 1", max_length=255)),
            ],
        ),
    ]
