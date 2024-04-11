from django.db import models
from django.urls import reverse


# class ExistsManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(deleted_at__isnull=True)


class Product(models.Model):

    class WeightType(models.IntegerChoices):
        WEIGHED = 0, 'переменный'
        FIXED = 1, 'фиксированный'

    fish = models.CharField(max_length=50, verbose_name='Название рыбы')
    cutting = models.CharField(max_length=10, blank=True, verbose_name='Разделка')
    size = models.CharField(max_length=15, blank=True, verbose_name='Размер')
    producer = models.CharField(max_length=50, blank=True, verbose_name='Производитель')
    package = models.CharField(max_length=15, blank=True, default='мешок', verbose_name='Упаковка')
    fixed_weight = models.BooleanField(choices=WeightType.choices, default=WeightType.FIXED, blank=False, verbose_name='Маркировка веса')
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Вес')
    note = models.TextField(blank=True)
    date_create = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    date_update = models.DateField(auto_now=True, verbose_name='Дата изменения')

    objects = models.Manager()
    # exists = ExistsManager()

    def get_absolute_url(self):
        return reverse('products:product', kwargs={'pk': self.pk})


    def __str__(self):
        return f"{self.fish} {self.cutting} {self.size} \"{self.producer}\" ({self.pk}id) {self.weight if self.weight else '-'}кг"

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['fish', 'cutting', 'size']