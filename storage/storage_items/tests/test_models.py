from django.test import TestCase
# class NotZeroManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(~Q(available=0) | ~Q(stored=0))
#
# class AvailableManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(~Q(available=0))
#
#
# class StorageItem(models.Model):
#     product = models.ForeignKey(
#         'products.Product',
#         on_delete=models.PROTECT, null=True,
#         related_name='storage_items',
#         verbose_name='Продукт')
#     weight = models.DecimalField(default=1, null=False, max_digits=7, decimal_places=2)
#     price = models.DecimalField(default=0, null=False, max_digits=7, decimal_places=2)
#     available = models.DecimalField(default=0, null=False, max_digits=12, decimal_places=2)
#     stored = models.DecimalField(default=0, null=False, max_digits=12, decimal_places=2)
#
#     sellable = AvailableManager()
#     not_zero = NotZeroManager()
#     objects = models.Manager()
#
#     class Meta:
#         unique_together = [("product", "price", "weight")]
#
#     def __str__(self):
#         return f"{self.product} {self.weight}кг {self.price}руб: {self.available}/{self.stored}"

class TestStorageItemModel(TestCase):
    def setUp(self) -> None:
        pass

    # def test_labels(self):
    #     p = self.rus_object
    #     field_fish = p._meta.get_field('fish').verbose_name
    #     field_cutting = p._meta.get_field('cutting').verbose_name
    #     field_size = p._meta.get_field('size').verbose_name
    #     field_producer = p._meta.get_field('producer').verbose_name
    #     field_package = p._meta.get_field('package').verbose_name
    #     field_note = p._meta.get_field('note').verbose_name
    #     field_date_create = p._meta.get_field('date_create').verbose_name
    #     field_date_update = p._meta.get_field('date_update').verbose_name
    #     self.assertEqual(field_fish, 'Название рыбы')
    #     self.assertEqual(field_cutting, 'Разделка')
    #     self.assertEqual(field_size, 'Размер')
    #     self.assertEqual(field_producer, 'Производитель')
    #     self.assertEqual(field_package, 'Упаковка')
    #     self.assertEqual(field_note, 'Заметки')
    #     self.assertEqual(field_date_create, 'Дата создания')
    #     self.assertEqual(field_date_update, 'Дата изменения')
    #
    # def test_constraints_indication(self):
    #     p = self.rus_object
    #     field_fish = p._meta.get_field('fish').max_length
    #     field_cutting = p._meta.get_field('cutting').max_length
    #     field_size = p._meta.get_field('size').max_length
    #     field_producer = p._meta.get_field('producer').max_length
    #     field_package = p._meta.get_field('package').max_length
    #
    #     self.assertEqual(field_fish, 50)
    #     self.assertEqual(field_cutting, 15)
    #     self.assertEqual(field_size, 15)
    #     self.assertEqual(field_producer, 50)
    #     self.assertEqual(field_package, 15)
    #
    # def test_objects_created(self):
    #     queryset_all = Product.objects.all()
    #     self.assertEquals(queryset_all.count(), 7)
    #
    # def test_objects_pk_incremented(self):
    #     self.assertEquals(Product.objects.get(fish='Salmon').pk, 1)
    #     self.assertEquals(Product.objects.get(fish='Sardine').pk, 2)
    #     self.assertEquals(Product.objects.get(fish='Pollock').pk, 3)
    #     self.assertEquals(Product.objects.get(fish='Shrimp').pk, 4)
    #     self.assertEquals(Product.objects.get(fish='Crab sticks').pk, 5)
    #
    # def test_auto_assigning(self):
    #     p1 = Product.objects.get(fish='Salmon')
    #     self.assertEquals(p1.cutting, '')
    #     self.assertEquals(p1.size, '')
    #     self.assertEquals(p1.producer, '')
    #     self.assertEquals(p1.package, '')
    #     self.assertEquals(p1.note, '')
    #     self.assertEquals(p1.date_create, date.today())
    #     self.assertEquals(p1.date_update, date.today())
    #
    # def test_cyrillic_chars(self):
    #     p1 = Product.objects.get(fish='Кижуч')
    #     self.assertEquals(p1.cutting, 'НР')
    #     self.assertEquals(p1.size, '2+кг')
    #     self.assertEquals(p1.producer, 'Алаид')
    #     self.assertEquals(p1.package, 'мешок')
    #     self.assertTrue(p1.note)
    #
    # def test_numeric_chars(self):
    #     self.assertTrue(Product.objects.filter(fish='111').exists())
    #     p1 = Product.objects.get(fish='111')
    #     self.assertEquals(p1.cutting, '111')
    #     self.assertEquals(p1.size, '111')
    #     self.assertEquals(p1.producer, '111')
    #     self.assertEquals(p1.package, '111')
    #     self.assertEquals(p1.note, '111')
    #
    # def test_related_objects(self):
    #     contractor = Contractor.objects.create(name='ООО Алаид')
    #     contract = Contract.objects.create(
    #         contract_type='income',
    #         date_plan=date.today(),
    #         contractor=contractor
    #     )
    #     specification1 = Specification.objects.create(
    #         contract=contract,
    #         product=self.product1,
    #         variable_weight=18,
    #         price=500,
    #         quantity=1000,
    #     )
    #     specification2 = Specification.objects.create(
    #         contract=contract,
    #         product=self.product1,
    #         variable_weight=1,
    #         price=800,
    #         quantity=1000,
    #     )
    #     specification3 = Specification.objects.create(
    #         contract=contract,
    #         product=self.product2,
    #         variable_weight=1,
    #         price=800,
    #         quantity=1000,
    #     )
    #     storage_item = StorageItem.objects.create(
    #         product=self.product1,
    #         weight=18,
    #         price=500,
    #         available=1000,
    #         stored=1000,
    #     )
    #
    #     self.assertEquals(self.product1.specifications.all().count(), 2)
    #     self.assertEquals(self.product2.specifications.all().count(), 1)
    #     self.assertEquals(self.product1.storage_items.all().count(), 1)
    #     self.assertEquals(storage_item.product, self.product1)
    #     self.assertEquals(specification1.product, self.product1)
    #     self.assertEquals(specification3.product, self.product2)
    #     self.assertTrue(contract.specifications.filter(product=self.product1).exists())
    #
    # def test_update_object(self):
    #     p_before = Product.objects.filter(pk=1)[0]
    #     Product.objects.filter(pk=1).update(cutting='uncut')
    #     p_after = Product.objects.filter(pk=1)[0]
    #     self.assertTrue(p_before == p_after)
    #     self.assertFalse(p_before.cutting == p_after.cutting)
    #     self.assertNotEquals(p_before.cutting, p_after.cutting)
    #     self.assertEquals(p_after.cutting, 'uncut')
    #
    # def test_model_save(self):
    #     p = Product.objects.create(fish='Сельдь', note='хранение 9 мес')
    #     p.save()
    #     saved_model = Product.objects.get(fish='Сельдь')
    #     self.assertEqual(saved_model.note, 'хранение 9 мес')
    #
    # def test_delete_object(self):
    #     p = Product.objects.create(fish='Herring')
    #     p.save()
    #     p_found = Product.objects.get(fish='Herring')
    #     self.assertEquals(p_found.pk, 8)
    #     p_found.delete()
    #     with self.assertRaises(Product.DoesNotExist):
    #         Product.objects.get(fish='Herring')
    #
    # def test_constraints(self):
    #     p1 = Product.objects.create()
    #     p2 = Product.objects.create(fish=('ф' * 60))
    #     p3 = Product.objects.create(
    #         fish='1' * 120,
    #         cutting='1' * 120,
    #         size='1' * 120,
    #         producer='1' * 120,
    #         package='1' * 120,
    #         note='1' * 120
    #     )
    #     p4 = Product.objects.create(fish='example', cutting='1' * 16)
    #     p5 = Product.objects.create(fish='example', size='1' * 16)
    #     p6 = Product.objects.create(fish='example', producer='1' * 51)
    #     p7 = Product.objects.create(fish='example', package='1' * 16)
    #
    #     p1_after = Product.objects.filter(fish__exact='')[0]
    #     p2_after = Product.objects.filter(fish__contains='ффф')[0]
    #     p3_after = Product.objects.filter(fish__contains='11111')[0]
    #     self.assertEquals(len(p1_after.fish), 0)
    #     self.assertEquals(len(p2_after.fish), 60)
    #     self.assertEquals(len(p3_after.fish), 120)
    #
    #     with self.assertRaises(ValidationError) as e1:
    #         p1_after.full_clean()
    #     self.assertEquals(e1.exception.messages, ['Это поле не может быть пустым.'])
    #     with self.assertRaises(ValidationError) as e2:
    #         p2_after.full_clean()
    #     self.assertEquals(len(e2.exception.messages), 1)
    #     with self.assertRaises(ValidationError) as e3:
    #         p3_after.full_clean()
    #     self.assertEquals(len(e3.exception.messages), 5)
    #
    #     with self.assertRaises(ValidationError) as e4:
    #         p4.full_clean()
    #     self.assertEquals(e4.exception.messages,
    #                       ['Убедитесь, что это значение содержит не более 15 символов (сейчас 16).'])
    #     with self.assertRaises(ValidationError) as e5:
    #         p5.full_clean()
    #     self.assertEquals(e5.exception.messages,
    #                       ['Убедитесь, что это значение содержит не более 15 символов (сейчас 16).'])
    #     with self.assertRaises(ValidationError) as e6:
    #         p6.full_clean()
    #     self.assertEquals(e6.exception.messages,
    #                       ['Убедитесь, что это значение содержит не более 50 символов (сейчас 51).'])
    #     with self.assertRaises(ValidationError) as e7:
    #         p7.full_clean()
    #     self.assertEquals(e7.exception.messages,
    #                       ['Убедитесь, что это значение содержит не более 15 символов (сейчас 16).'])
    #
    # def test_absolute_url(self):
    #     self.assertEquals(self.product1.get_absolute_url(), '/products/' + str(self.product1.pk) + '/')
    #
    # def test_string_representation(self):
    #     p = self.product1
    #     self.assertEquals(str(self.product1), f"{p.fish} {p.cutting} {p.size} \"{p.producer}\" ({p.pk}id)")
    #
