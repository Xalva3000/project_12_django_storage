import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from products.utils import contract_re_map, insert_action_notification

from contracts.models import Contract, Payment
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
        storage_item = StorageItem.objects.get_or_create(product=specification.product,
                                                         weight=specification.variable_weight,
                                                         price=specification.price)[0]
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
        storage_item = StorageItem.objects.get(product=specification.product,
                                               weight=specification.variable_weight,
                                               price=specification.price)
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
    operation = False
    stage = 'reserve'
    if specifications.count() > 0:
        if contract.contract_type == Contract.ContractType.INCOME:
            if re == '00':
                operation = 'apply'
                switch_income_reserve_stage(contract=contract, operation=operation)
            elif re == '10':
                operation = 'cancel'
                switch_income_reserve_stage(contract=contract, operation=operation)
        else:
            if re == '10':
                operation = 'cancel'
                switch_outcome_stage(contract=contract, stage=stage, operation=operation)
                contract.reserved = False

            elif re == '00':
                operation = 'apply'
                switch_outcome_stage(contract=contract, stage=stage, operation=operation)
                contract.reserved = True

    if operation:
        action = 'reserved' if operation == 'apply' else 'unreserved'
        insert_action_notification(contract=contract, action=action)
        contract.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)


@login_required
def switch_payment_by_contract_id(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if contract.specifications.all():
        action = 'unpaid' if contract.paid else 'paid'
        contract.paid = not contract.paid
        contract.save()
        insert_action_notification(contract=contract, action=action)
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)


@login_required
def switch_execution_by_contract_id(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    specifications = contract.specifications.all()
    re = contract_re_map(contract)
    operation = False
    stage = 'execution'
    if specifications and re in ('10', '11'):

        if contract.contract_type == Contract.ContractType.INCOME:
            if re == '10':
                operation = 'apply'
                switch_income_execution_stage(contract=contract, operation=operation)
            elif re == '11':
                operation = 'cancel'
                switch_income_execution_stage(contract=contract, operation=operation)
        if contract.contract_type == Contract.ContractType.OUTCOME:
            if re == '10':
                operation = 'apply'
                switch_outcome_stage(contract=contract, stage=stage, operation=operation)
                # contract.date_plan = datetime.date.today()
                contract.date_execution = datetime.date.today()
            elif re == '11':
                operation = 'cancel'
                switch_outcome_stage(contract=contract, stage=stage, operation=operation)
                contract.date_execution = None

    if operation:
        action = 'executed' if operation == 'apply' else 'unexecuted'
        insert_action_notification(contract=contract, action=action)
        contract.executed = not contract.executed
        contract.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)


@login_required
def delete_contract(request, pk):
    contract = Contract.objects.get(pk=pk)
    re = contract_re_map(contract)
    action = False
    if re == '00' and not contract.date_delete:
        action = 'deleted'
        contract.date_delete = datetime.date.today()
    elif re == '00' and contract.date_delete:
        action = 'undeleted'
        contract.date_delete = None

    if action:
        insert_action_notification(contract=contract, action=action)
        contract.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)


def change_manager_share(request, pk):
    new_share = int(request.POST.get('new_share', 0))
    contract = Contract.objects.get(pk=pk)
    contract.manager_share = new_share
    contract.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)


def change_note(request, pk):
    new_note = request.POST.get('new_note', '')
    contract = Contract.objects.get(pk=pk)
    contract.note = new_note
    contract.save()
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)


def add_payment(request, pk):
    action = 'new_payment'
    amount = int(request.POST.get(action, 0))
    payment = Payment.objects.create(contract_id=pk, amount=amount)
    payment.save()
    insert_action_notification(contract=pk, action=action, extra_info=amount)
    uri = reverse('contracts:contract', kwargs={'pk': pk})
    return redirect(uri)


# def delete_payment(request, pk):
#     new_share = int(request.POST.get('new_share', 0))
#     contract = Contract.objects.get(pk=pk)
#     contract.
#     contract.save()
#     uri = reverse('contracts:contract', kwargs={'pk': pk})
#     return redirect(uri)
