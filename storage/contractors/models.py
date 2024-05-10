from django.db import models
from django.urls import reverse


class Contractor(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, verbose_name='Название')
    address = models.CharField(max_length=200, blank=True, verbose_name='Адрес')
    email = models.EmailField(max_length=50, blank=True, verbose_name='E-mail')
    contact_data = models.TextField(blank=True, verbose_name='Контакты')
    date_create = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    date_update = models.DateField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return f'{self.pk}id: {self.name} {self.address}'

    def get_absolute_url(self):
        return reverse('contractors:contractor', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'
        ordering = ['name', 'address', 'date_create']
