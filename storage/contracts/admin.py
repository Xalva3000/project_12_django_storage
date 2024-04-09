from django.contrib import admin

from .models import Contract, Specification


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    fields = ['contract_type', 'date_plan',
              'reserved', 'paid', 'executed',
              'note', 'date_execution', 'date_delete',
              'contractor']
    list_display = ('id', 'contract_type', 'contractor',
                    'date_plan', 'date_create', 'date_delete')
    readonly_fields = ['date_create', 'reserved', 'paid', 'executed', ]
    list_display_links = ('contractor',)
    ordering = ['contract_type', 'contractor', 'date_create', 'id']
    list_per_page = 8
    search_fields = ['contractor', 'date_create']


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    fields = ['contract', 'product', 'quantity', 'price']
    list_display = ('id', 'contract', 'product', 'quantity', 'price')
    readonly_fields = []
    list_display_links = ('product',)
    ordering = ['contract']
    list_per_page = 8
# search_fields = []
