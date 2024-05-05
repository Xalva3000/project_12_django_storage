
from django.shortcuts import get_object_or_404

from contracts.models import Contract, Action
from django.urls import reverse_lazy

menu = [{'title': "Продукты", 'url_name': 'products:products'},
        {'title': "Контрагенты", 'url_name': 'contractors:contractors'},
        {'title': "Контракты", 'url_name': 'contracts:contracts'},
        {'title': "Склад", 'url_name': 'storage_items:not_zero'},
        ]

tools = {
    "products": [{'title': "Список", 'path': 'products:products'},
                 {'title': "Добавить", 'path': 'products:add_product'}, ],
    "contractors": [{'title': "Список", 'path': 'contractors:contractors'},
                    {'title': "Добавить", 'path': 'contractors:add_contractor'}, ],
    "contracts": [{'title': 'Список', 'path': 'contracts:contracts'},
                  {'title': "Список+", 'path': 'contracts:contracts_plus'},
                  {'title': "Добавить", 'path': 'contracts:add_contract'},
                  {'title': "Удаленные", 'path': 'contracts:contracts_deleted'}, ],
    "storage_items": [{'title': 'Список', 'path': 'storage_items:not_zero'},
                      {'title': 'К продаже', 'path': 'storage_items:available'},],
}


class DataMixin:
    title_page = None
    category_page = None
    menu_selected = None
    tool_selected = None
    extra_context: dict[str, str | int] = {}

    def __init__(self):
        if self.title_page:
            self.extra_context['title'] = self.title_page
        if self.menu_selected is not None:
            self.extra_context['menu_selected'] = self.menu_selected
        if self.tool_selected is not None:
            self.extra_context['tool_selected'] = self.tool_selected

    def get_mixin_context(self, context, **kwargs):
        # context['menu'] = menu
        if self.category_page:
            context['tools'] = tools[self.category_page]
        context['custom_url'] = self.cut_page_from_url(self.request.get_full_path())
        context.update(kwargs)
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)

    @staticmethod
    def cut_page_from_url(string):
        if 'page' in string:
            return string.rsplit('page', 1)[0]
        elif '?' in string:
            return string + '&'
        else:
            return '?'


def contract_re_map(contract):
    return ''.join(map(lambda b: str(int(b)), [contract.reserved, contract.executed]))


def contract_rpe_map(contract):
    return ''.join(map(lambda b: str(int(b)), [contract.reserved, contract.executed, contract.paid]))


def insert_action_notification(contract: int | Contract, action: str, extra_info=None):
    if isinstance(contract, int):
        contract = get_object_or_404(Contract, pk=contract)
    dct = {
        'created': f'Создан {contract.pk}-{contract.contractor.name} // {extra_info}.',
        'deleted': f'Удален {contract.pk}-{contract.contractor.name}.',
        'undeleted': f'Восстановлен {contract.pk}-{contract.contractor.name}.',
        'reserved': f'Бронь {contract.pk}-{contract.contractor.name}.',
        'unreserved': f'Снята бронь {contract.pk}-{contract.contractor.name}.',
        'paid': f'Оплачен {contract.pk}-{contract.contractor.name}.',
        'unpaid': f'Неоплачен {contract.pk}-{contract.contractor.name}.',
        'executed': f'Отгрузка {contract.pk}-{contract.contractor.name}.',
        'unexecuted': f'Возврат {contract.pk}-{contract.contractor.name}.',
        'new_payment': f'Платеж {contract.pk}-{contract.contractor.name}.',
        'new_change': f'Изменение {contract.pk}-{contract.contractor.name}.',
    }
    if action in dct:
        message = dct.get(action, 'message_error')
        new_action = Action.objects.create(contract=contract, action=message)
        new_action.save()



