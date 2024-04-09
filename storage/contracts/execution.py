import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from products.utils import contract_re_map

from contracts.models import Contract
from storage_items.models import StorageItem


class OperationError(ValueError):
    pass


def switch_income_reserve_stage(contract, *, operation: str = 'apply'):
    """
    contract :: Contract(model) object with specifications
    operation :: str = 'apply' or 'cancel'. """
    demand = {
        'apply': {'available': lambda s_i, num: s_i.available + num},
        'cancel': {'available': lambda s_i, num: s_i.available - num,}
    }
    specifications = contract.specifications.all()
    for specification in specifications:
        storage_item = StorageItem.objects.get_or_create(product=specification.product, price=specification.price)[0]
        storage_item.available = demand[operation]['available'](storage_item, specification.quantity)
        storage_item.save()
    contract.reserved = operation == 'apply'


def switch_income_execution_stage(contract, *, operation: str = 'apply'):
    """
    contract :: Contract(model) object with specifications
    operation :: str = 'apply' or 'cancel'. """
    demand = {
        'apply': lambda s_i, num: s_i.stored + num,
        'cancel': lambda s_i, num: s_i.stored - num
    }
    specifications = contract.specifications.all()
    for specification in specifications:
        storage_item = StorageItem.objects.get(product=specification.product, price=specification.price)
        storage_item.stored = demand[operation](storage_item, specification.quantity)
        storage_item.save()
    # contract.date_plan = datetime.date.today()
    contract.date_execution = datetime.date.today() if operation == 'apply' else None


def switch_outcome_stage(contract, *, stage: str = 'reserve', operation: str = 'apply'):
    """
        contract:: Contract(model) object with specifications
        stage:: str 'reserve' or 'payment' or 'execution'
        operation:: str = 'apply' or 'cancel'. """
    demand = {('reserve', 'apply'): lambda specification: specification.storage_item.available - specification.quantity,
             ('execution', 'apply'): lambda specification: specification.storage_item.stored - specification.quantity,
             ('reserve', 'cancel'): lambda specification: specification.storage_item.available + specification.quantity,
             ('execution', 'cancel'): lambda specification: specification.storage_item.stored + specification.quantity,}
    specifications = contract.specifications.all()
    for specification in specifications:
        if stage == 'reserve':
            specification.storage_item.available = demand[(stage, operation)](specification)
        elif stage == 'execution':
            specification.storage_item.stored = demand[(stage, operation)](specification)
        specification.storage_item.save()

@login_required
def switch_reserve_by_contract_id(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    re = contract_re_map(contract)
    specifications = contract.specifications.all()
    if specifications.count() > 0:
        if contract.contract_type == Contract.ContractType.INCOME:
            if re == '00':
                switch_income_reserve_stage(contract=contract, operation='apply')
            elif re == '10':
                switch_income_reserve_stage(contract=contract, operation='cancel')
        else:
            if re == '10':
                switch_outcome_stage(contract=contract, stage='reserve', operation='cancel')
                contract.reserved = False

            elif re == '00':
                switch_outcome_stage(contract=contract, stage='reserve', operation='apply')
                contract.reserved = True

        contract.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)

@login_required
def switch_payment_by_contract_id(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if contract.specifications.all():
        contract.paid = not contract.paid
        contract.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)


@login_required
def switch_execution_by_contract_id(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    specifications = contract.specifications.all()
    re = contract_re_map(contract)
    if specifications and re in ('10', '11'):

        if contract.contract_type == Contract.ContractType.INCOME:
            if re == '10':
                switch_income_execution_stage(contract=contract, operation='apply')
            elif re == '11':
                switch_income_execution_stage(contract=contract, operation='cancel')
        if contract.contract_type == Contract.ContractType.OUTCOME:
            if re == '10':
                switch_outcome_stage(contract=contract, stage='execution', operation='apply')
                # contract.date_plan = datetime.date.today()
                contract.date_execution = datetime.date.today()
            elif re == '11':
                switch_outcome_stage(contract=contract, stage='execution', operation='cancel')
                contract.date_execution = None

        contract.executed = not contract.executed
        contract.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)

@login_required
def delete_contract(request, pk):
    contract = Contract.objects.get(pk=pk)
    re = contract_re_map(contract)
    if re == '00' and not contract.date_delete:
        contract.date_delete = datetime.date.today()
        contract.save()
    elif re == '00' and contract.date_delete:
        contract.date_delete = None
        contract.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)