from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.shortcuts import render
from django.views.generic import ListView

from .models import StorageItem
from products.utils import DataMixin


# Create your views here.
class StorageItemsList(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'storage_items/storage_items.html'
    context_object_name = 'storage_items'
    # allow_empty = False
    title_page = 'Склад'
    category_page = 'storage_items'
    paginate_by = 100

    def get_queryset(self):
        return StorageItem.not_zero.order_by('product__fish', 'price')


class StorageItemsGroupList(LoginRequiredMixin, DataMixin, ListView):
    template_name = 'storage_items/storage_items.html'
    context_object_name = 'storage_items'
    allow_empty = False
    title_page = 'Склад'
    category_page = 'storage'
    paginate_by = 100

    def get_queryset(self):
        return StorageItem.objects.values('product').annotate(
            available=Sum('available'), stored=Sum('stored'))