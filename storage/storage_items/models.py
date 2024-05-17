from django.db import models
from django.db.models import Q


class NotZeroManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(~Q(available=0) | ~Q(stored=0))


class AvailableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(~Q(available=0))


class StorageItem(models.Model):
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        related_name='storage_items',
        verbose_name='Продукт')
    weight = models.DecimalField(default=1, null=False, max_digits=7, decimal_places=2)
    price = models.DecimalField(default=0, null=False, max_digits=7, decimal_places=2)
    available = models.DecimalField(default=0, null=False, max_digits=12, decimal_places=2)
    stored = models.DecimalField(default=0, null=False, max_digits=12, decimal_places=2)

    sellable = AvailableManager()
    not_zero = NotZeroManager()
    objects = models.Manager()

    class Meta:
        unique_together = [("product", "price", "weight")]

    def __str__(self):
        return f"{self.product} {self.weight}кг {self.price}руб: {self.available}/{self.stored}"


# Проверка валидации полей модели:
# Напишите тесты, чтобы убедиться, что поля weight, price, available и stored
# корректно валидируют входные данные, включая проверку стандартных значений,
# минимальных и максимальных допустимых значений.
#
# Тестирование методов модели:
# Напишите тесты для метода __str__(), чтобы убедиться, что он возвращает
# корректное строковое представление объекта StorageItem.
# Если у вас есть пользовательские менеджеры (AvailableManager и NotZeroManager),
# напишите тесты для гарантии их корректной работы.
#
# Проверка метаданных полей:
# Напишите тесты для проверки того, что уникальное свойство было правильно
# задано в метаклассе модели StorageItem.
#
# Тестирование связей модели:
# Убедитесь, что связь ForeignKey между StorageItem и Product устанавливается
# и удаляется правильно (вы можете использовать фиктивные объекты или моки
# для наглядности).
#
# Тестирование методов объекта:
# Если у вас есть методы объекта, которые выполняют сложные операции над
# объектом StorageItem, напишите тесты для проверки их функциональности.
#
# Моделирование уникальных случаев:
# Напишите тесты для моделирования специальных случаев, например, когда
# значения полей равны или близки к их граничным значениям (например, для
# ситуаций, когда количество доступных товаров равно нулю, или для разных
# значений цены и веса при тестировании уникальной валидации).