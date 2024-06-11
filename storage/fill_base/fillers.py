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
    storage_item=StorageItem.objects.get(product=spec.product,
                                            price=spec.price,
                                            weight=spec.variable_weight),
    price=spec.price + choice([20,50,100]),
    quantity=choices(sorted(filter(lambda num: num <= spec.quantity, quantity_list))[-2::], [10, 90])[0]
) for spec in c.specifications.all()
    if StorageItem.objects.filter(product=spec.product, price=spec.price, weight=spec.variable_weight).exists()]
    for c in contracts_income]

specifications_outcome = [Specification.objects.create(
    contract=choice(contracts_outcome),
    storage_item=si,
    variable_weight=si.weight,
    price=si.price + 100,
    quantity=si.available
) for si in StorageItem.not_zero.all()]

[c.date_delete=date.today() for c in contracts_outcome if not c.specifications.all().exists()]

for c in contracts_outcome:
    if not c.specifications.all().exists():
        c.date_delete = date.today()


[switch_reserve(c.pk) for c in contracts_outcome if c.date_delete is None]
[switch_execution(c.pk) for c in Contract.objects.filter(date_delete=None, contract_type=Contract.ContractType.OUTCOME)]

[Payment.objects.create(
    contract=c,
    amount=int(c.specifications.aggregate(sum=Sum(F('price') * F('variable_weight') * F('quantity')))['sum'])
) for c in contracts_income]

[Payment.objects.create(
    contract=c,
    amount=int(c.specifications.aggregate(sum=Sum(F('price') * F('variable_weight') * F('quantity')))['sum'])
) for c in Contract.objects.filter(date_delete=None, contract_type=Contract.ContractType.OUTCOME)]

[switch_payment(c.pk) for c in Contract.objects.filter(contract_type=Contract.ContractType.OUTCOME) if c.executed]

for c in Contract.objects.filter(date_delete=None):
    c.manager_share = c.specifications.aggregate(w=Sum(F('variable_weight') * F('quantity')))['w'] * 5
    c.save()
