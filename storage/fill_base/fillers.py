from names import *


contractors_income = [
    Contractor.objects.create(
        name=company_list.pop(),
        email=email_list.pop(),
        address=city_list.pop()
    ) for _ in range(50)]

contractors_outcome = [
    Contractor.objects.create(
        name=company_list.pop(),
        email=email_list.pop(),
        address=city_list.pop()
    ) for _ in range(100)]

products = [Product.objects.create(
    fish=v[0],
    cutting=v[1],
    size=v[2]) for v in product_variants if Product.objects.filter(
    fish=v[0],
    cutting=v[1],
    size=v[2]).exists() == False]

contracts_income = [
    Contract.objects.create(
        contractor=choice(contractors_income),
        contract_type=Contract.ContractType.INCOME,
        date_plan=choice(date_list),
        note=''
    ) for _ in range(500)]

specifications_income = [[Specification.objects.create(
    contract=c,
    product=choice(products),
    variable_weight=choice(weight_list),
    price=choice(price_list),
    quantity=choice(quantity_list)
) for _ in range(choice(range(1,6)))] for c in contracts_income]

[switch_reserve(c.pk) for c in contracts_income]
[switch_execution(c.pk) for c in contracts_income]

[Payment.objects.create(
    contract=c,
    amount=int(
        c.specifications.aggregate(
            sum=Sum(F('price') * F('variable_weight') * F('quantity')))['sum']
    )
) for c in contracts_income]

[switch_payment(c.pk) for c in contracts_income]

contracts_outcome = [Contract.objects.create(
    contractor=choice(contractors_outcome),
    contract_type=Contract.ContractType.OUTCOME,
    date_plan=c.date_plan + timedelta(days=choice(range(1,6))),
    note='') for c in contracts_income]

specifications_outcome = [[Specification.objects.create(
    contract=choice(Contract.objects.filter(date_plan__gt=c.date_plan, contract_type=Contract.ContractType.OUTCOME)),
    storage_item=StorageItem.objects.filter(product=spec.product,
                                            price=spec.price,
                                            weight=spec.variable_weight)[0],
    price=spec.price + choice([20,50,100]),
    quantity=choices(sorted(filter(lambda num: num <= spec.quantity, quantity_list))[-2::], [10, 90])[0]
) for spec in c.specifications.all()
    if StorageItem.objects.filter(product=spec.product, price=spec.price, weight=spec.variable_weight).exists()]
    for c in contracts_income]

[switch_reserve(c.pk) for c in contracts_outcome]
[switch_execution(c.pk) for c in contracts_outcome]

[Payment.objects.create(
    contract=c,
    amount=int(c.specifications.aggregate(sum=Sum(F('price') * F('variable_weight') * F('quantity')))['sum'])
) for c in contracts_income]
[Payment.objects.create(
    contract=c,
    amount=int(c.specifications.aggregate(sum=Sum(F('price') * F('variable_weight') * F('quantity')))['sum'])
) for c in Contract.objects.filter(contract_type=Contract.ContractType.OUTCOME) if c.specifications.all().exists()]

[switch_payment(c.pk) for c in Contract.objects.filter(contract_type=Contract.ContractType.OUTCOME) if c.executed]

# [switch_execution(c.pk) for c in Contract.objects.filter(date_create=date.today())]
# [Payment.objects.create(contract=c, amount=int(
#     c.specifications.aggregate(sum=Sum(F('price') * F('variable_weight') * F('quantity')))['sum'])) for c in
#  Contract.objects.filter(date_create=date.today())]
# [switch_payment(c.pk) for c in Contract.objects.filter(date_create=date(2024,6,8)))]

# contracts_outcome = [Contract.objects.create(contractor=choice(Contractor.objects.filter(pk__in=range(100,167))),
#                                              contract_type=Contract.ContractType.OUTCOME,
#                                              date_plan=c.date_plan + timedelta(days=choice(range(5)))) for c in
#                      Contract.objects.filter(date_create=date(2024,6,8))]


# from random import choices


# specifications_outcome = [[Specification.objects.create(contract=c,
#                                                        storage_item=StorageItem.objects.filter(product=spec.product,
#                                                                                                price=spec.price,
#                                                                                                weight=spec.variable_weight)[
#                                                            0],
#                                                        price=spec.price + choice([20,50,100]),
#                                                        quantity=choice(list(filter(lambda num: num <= spec.quantity, quantity_list))[-2::])) for spec in c.specifications.all()]
#                           for c in Contract.objects.filter(date_create=date(2024,6,8))]

# [client.get(reverse('contracts:contract_reserve', args=[c.pk])) for c in contracts_outcome]
# [client.get(reverse('contracts:contract_execution', args=[c.pk])) for c in contracts_outcome]
# [switch_reserve(c.pk) for c in  Contract.objects.filter(Q(date_create=date(2024,6,8)) & Q(contract_type=Contract.ContractType.OUTCOME)))]



