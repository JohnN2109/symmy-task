from django.db import models


class ProductSync(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    hash = models.CharField(max_length=64)
    updated_at = models.DateTimeField(auto_now=True)