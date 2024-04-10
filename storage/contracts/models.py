import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from pydantic import BaseModel
from datetime import date



class Contract(models.Model):
    class ContractType(models.TextChoices):
        INCOME = 'Покупка'
        OUTCOME = 'Продажа'

    contract_type = models.CharField(max_length=7, choices=ContractType, default=ContractType.OUTCOME)
    date_plan = models.DateField(default=datetime.date.today)
    reserved = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    executed = models.BooleanField(default=False)
    note = models.TextField(blank=True)
    date_create = models.DateField(auto_now_add=True)
    date_execution = models.DateField(blank=True, null=True)
    date_delete = models.DateField(blank=True, null=True)
    manager_share = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True, default=0)

    contractor = models.ForeignKey('contractors.Contractor', on_delete=models.PROTECT,
                                   null=True, related_name='contracts')
    manager = models.ForeignKey(get_user_model(), on_delete=models.PROTECT,
                                related_name='contracts', null=True, default=None)

    def __str__(self):
        return f"{self.pk} {self.contract_type} {self.contractor.name} {self.reserved} {self.executed} {self.paid}"


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
    variable_weight = models.DecimalField(decimal_places=2, max_digits=7, blank=False, null=False, default=1)
    quantity = models.IntegerField(default="0", blank=False, null=False)
    price = models.DecimalField(decimal_places=2, max_digits=7, blank=False, null=False, default=0)
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.PROTECT, null=True,
        related_name='specifications',
        verbose_name='Контракт')
    date_create = models.DateField(auto_now_add=True)
    date_update = models.DateField(auto_now=True)

    def __str__(self):
        weight = ''.join(['(', str(self.variable_weight), 'кг)'])
        if self.product:
            look = f"{self.product.fish} {self.product.cutting} " \
                   f"{self.product.size} {self.product.producer}:: " \
                    f"{weight} x {self.quantity} = {self.variable_weight * self.quantity:,.0f}кг по {self.price}р"
        elif self.storage_item:
            look = f"{self.storage_item.product.fish} {self.storage_item.product.cutting} " \
                   f"{self.storage_item.product.size} {self.storage_item.product.producer}" \
                   f" (закуп:{self.storage_item.price})::{weight} X {self.quantity}=" \
                   f"{self.variable_weight*self.quantity:,.0f}кг по {self.price}р"
        return look


class Payments(models.Model):
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.PROTECT, null=True,
        related_name='payments',
        verbose_name='Платежи')
    date_payment = models.DateField(auto_now_add=True, null=False)
    amount = models.DecimalField(decimal_places=2, max_digits=10, blank=False, null=False, default=0)

    def __str__(self):
        return f"{self.contract.pk} {self.date_payment} {self.amount}руб."
