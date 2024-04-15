from django.db import models
from django.db.models import Q


# Create your models here.

class NotZeroManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(~Q(available=0) | ~Q(stored=0))


class StorageItem(models.Model):
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT, null=True,
        related_name='product_name',
        verbose_name='Продукт')
    weight = models.DecimalField(default=1, null=False, max_digits=7, decimal_places=2)
    price = models.DecimalField(default=0, null=False, max_digits=7, decimal_places=2)
    available = models.DecimalField(default=0, null=False, max_digits=7, decimal_places=2)
    stored = models.DecimalField(default=0, null=False, max_digits=7, decimal_places=2)

    not_zero = NotZeroManager()
    objects = models.Manager()

    class Meta:
        unique_together = [("product", "price")]

    def __str__(self):
        return f"{self.product} {self.price}руб: {self.available}(available), {self.stored}(stored)"
