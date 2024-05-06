import django_filters
from django_filters.widgets import BooleanWidget, RangeWidget

from .models import Contract


# CHOICES = (
#             ("true", "Действующий"),
#             ("false", "Удаленный"),
#         )

class ContractFilter(django_filters.FilterSet):
    date_plan = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'placeholder': 'YYYY/MM/DD', 'type': 'date'}))
    specifications__product__fish = django_filters.CharFilter(label='Товар оприходования', lookup_expr='icontains')
    specifications__storage_item__product__fish = django_filters.CharFilter(label='Товар отгрузки', lookup_expr='icontains')
    contractor__name = django_filters.CharFilter(label='Контрагент', lookup_expr='icontains')
    manager__username = django_filters.CharFilter(label='Менеджер', lookup_expr='icontains')
    reserved = django_filters.BooleanFilter(label='Забронировано', )
    paid = django_filters.BooleanFilter(label='Оплачено', )
    executed = django_filters.BooleanFilter(label='Исполнено', )
    note = django_filters.CharFilter(label='В заметке:', lookup_expr='icontains')
    date_delete = django_filters.BooleanFilter(label='Действующий', lookup_expr='isnull', widget=BooleanWidget())

    class Meta:
        model = Contract
        fields = ['contract_type', 'contractor__name', 'date_plan',
                  'specifications__product__fish', 'specifications__storage_item__product__fish',
                  'reserved', 'paid', 'executed', 'note', 'date_delete']
