from django.contrib import admin

from .models import StorageItem


# Register your models here.
@admin.register(StorageItem)
class StorageItemAdmin(admin.ModelAdmin):
    fields = ['product', 'price', 'available', 'stored']
    list_display = ('id', 'product', 'price', 'available', 'stored')
    readonly_fields = []
    list_display_links = ('product',)
    ordering = ['product', 'id']
    list_per_page = 10
