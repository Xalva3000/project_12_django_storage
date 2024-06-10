from datetime import date
from itertools import product
from faker import Faker

fish_list = ['Минтай', 'Навага', 'Треска', 'Сельдь', 'Скумбрия', 'Корюшка', 'Камбала', 'Камбала икряная',
             'Палтус', 'Горбуша', 'Кета', 'Кижуч', 'Нерка', 'Лосось', 'Форель', 'Cемга', ]
cutting_list = ['ПБГ', 'НР', 'ПСГ', ]
size_list = ['S', 'M', 'L', '2L']
fake = Faker(['ru_RU'])
Faker.seed(1)
company_list = [fake.company() for _ in range(150)]
email_list = [fake.email() for _ in range(150)]
city_list = [fake.city() for _ in range(150)]
weight_list = [1, 15, 18, 20, 22, 22.5, 25]
price_list = [100, 300, 500, 600, 800, 1000]
quantity_list = [100, 150, 200, 337, 500, 800, 100]
date_list = [date.fromordinal(day) for day in range(date(2023, 6, 1).toordinal(), date(2024, 6, 15).toordinal()) if
             date.fromordinal(day).weekday() in range(0, 5)]

product_variants = list(product(fish_list, cutting_list, size_list))
