from django.conf import settings
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Cafe",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("address", models.TextField(blank=True)),
                ("phone", models.CharField(max_length=20, blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="CafeMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("staff", "Сотрудник кафе"), ("courier", "Курьер")], default="staff", max_length=20)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cafe_membership",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "cafe",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="members", to="order.cafe"),
                ),
            ],
            options={
                "unique_together": {("user", "role")},
            },
        ),
        migrations.AddField(
            model_name="order",
            name="cafe",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                to="order.cafe",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="courier",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="courier_orders",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="delivered_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="on_the_way_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="ready_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

