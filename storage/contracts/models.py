import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from decimal import Decimal

from django.urls import reverse


def decimal_validator(value):
    if not isinstance(value, Decimal):
        raise ValidationError("Variable must be Decimal")


def positive_validator(value):
    if value < 0:
        raise ValidationError("Variable must be positive")


class Contract(models.Model):
    class ContractType(models.TextChoices):
        INCOME = ('income', 'Покупка')
        OUTCOME = ('outcome', 'Продажа')

    contract_type = models.CharField(max_length=7, choices=ContractType,
                                     default=ContractType.OUTCOME, verbose_name='Тип контракта')
    date_plan = models.DateField(default=datetime.date.today, verbose_name='Планируемая дата исполнения')
    reserved = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    executed = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True, verbose_name='Заметки')
    date_create = models.DateField(auto_now_add=True)
    date_execution = models.DateField(blank=True, null=True)
    date_delete = models.DateField(blank=True, null=True)
    manager_share = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True, default=0)

    contractor = models.ForeignKey('contractors.Contractor', on_delete=models.PROTECT,
                                   null=True, related_name='contracts', verbose_name='Контрагент')
    manager = models.ForeignKey(get_user_model(), on_delete=models.PROTECT,
                                related_name='contracts', blank=True, null=True, default=None)

    def get_absolute_url(self):
        return reverse('contracts:contract', kwargs={'pk': self.pk})

    def __str__(self):
        russian_contract_type = 'Продажа' if self.contract_type == 'outcome' else 'Покупка'
        return f"{self.pk} {russian_contract_type} {self.contractor.name} " \
               f"({'1' if self.reserved else '0'}|{'1' if self.executed else '0'}|{'1' if self.paid else '0'})"


class Specification(models.Model):
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT, null=True,
        related_name='specifications',
        verbose_name='Закупка')
    storage_item = models.ForeignKey(
        'storage_items.StorageItem',
        on_delete=models.PROTECT, null=True,
        related_name='specifications',
        verbose_name='Товар со клада')
    variable_weight = models.DecimalField(validators=[decimal_validator, positive_validator],
                                          decimal_places=2, max_digits=7, blank=False, null=False, default=1)
    quantity = models.DecimalField(validators=[decimal_validator, positive_validator],
                                   decimal_places=2, max_digits=10, blank=False, null=False, default=1)
    price = models.DecimalField(validators=[decimal_validator, positive_validator],
                                decimal_places=2, max_digits=7, blank=False, null=False, default=0)
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.PROTECT, null=True,
        related_name='specifications',
        verbose_name='Контракт')
    date_create = models.DateField(auto_now_add=True)
    date_update = models.DateField(auto_now=True)

    def clean(self):
        if not self.product and not self.storage_item:
            raise ValidationError("Невозможно создание спецификации без указания продукта или складского объекта.")
        if self.product and self.storage_item:
            raise ValidationError("Невозможно создание спецификации с указанием продукта и складского объекта вместе.")

    def __str__(self):
        weight = ''.join(['(', str(self.variable_weight), 'кг)'])
        if self.product:
            look = f"{self.product.fish} {self.product.cutting} " \
                   f"{self.product.size} {self.product.producer}:: " \
                    f"{weight} x {self.quantity} = {self.variable_weight * self.quantity:,.2f}кг по {self.price}р"
        elif self.storage_item:
            look = f"{self.storage_item.product.fish} {self.storage_item.product.cutting} " \
                   f"{self.storage_item.product.size} {self.storage_item.product.producer}" \
                   f" (закуп:{self.storage_item.price})::{weight} X {self.quantity}=" \
                   f"{self.variable_weight*self.quantity:,.2f}кг по {self.price}р"
        return look


class Payment(models.Model):
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.PROTECT, null=True,
        related_name='payments',
        verbose_name='Платежи')
    date_payment = models.DateField(auto_now_add=True, null=False)
    amount = models.DecimalField(decimal_places=2, max_digits=10, blank=False, null=False, default=0)

    def __str__(self):
        return f"{self.contract.pk} {self.date_payment} {self.amount}руб."


class Action(models.Model):
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.PROTECT, null=True,
        related_name='actions',
        verbose_name='Действия')

    action = models.TextField(max_length=100)
    date_action = models.DateField(auto_now_add=True, null=False)

    def __str__(self):
        return f"{self.date_action}--{self.action}"
