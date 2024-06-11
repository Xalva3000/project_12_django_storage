from datetime import date

from contracts.execution import switch_income_reserve_stage, switch_outcome_stage, switch_income_execution_stage
from contracts.models import Contract
from products.utils import contract_re_map


def switch_reserve(pk):
    contract = Contract.objects.get(pk=pk)
    if contract.date_delete:
        return
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
        contract.save()
    return


def switch_execution(pk):
    contract = Contract.objects.get(pk=pk)
    if contract.date_delete:
        return
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
                contract.date_execution = date.today()
            elif re == '11':
                operation = 'cancel'
                switch_outcome_stage(contract=contract, stage=stage, operation=operation)
                contract.date_execution = None

    if operation:
        contract.executed = not contract.executed
        contract.save()
    return


def switch_payment(pk):
    contract = Contract.objects.get(pk=pk)
    if contract.date_delete:
        return
    if contract.specifications.all():
        contract.paid = not contract.paid
        contract.save()
    return


def replace_if_none(obj, new_obj):
    if obj is None:
        return new_obj
    return obj