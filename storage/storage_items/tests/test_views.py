# class StorageItemsList(LoginRequiredMixin, DataMixin, ListView):
#     template_name = 'storage_items/storage_items.html'
#     context_object_name = 'storage_items'
#     # allow_empty = False
#     title_page = 'Склад'
#     category_page = 'storage_items'
#     paginate_by = 100
#
#     def get_queryset(self):
#         return StorageItem.not_zero.annotate(weight_available=Sum(F('weight') * F('available')),
#                                              weight_stored=Sum(F('weight') * F('stored'))).order_by('product__fish', 'price')
#
#
# class StorageItemsAvailableList(LoginRequiredMixin, DataMixin, ListView):
#     template_name = 'storage_items/storage_items.html'
#     context_object_name = 'storage_items'
#     title_page = 'Склад'
#     category_page = 'storage_items'
#     paginate_by = 100
#
#     def get_queryset(self):
#         return StorageItem.sellable.annotate(weight_available=Sum(F('weight') * F('available')),
#                                              weight_stored=Sum(F('weight') * F('stored'))).order_by('product__fish', 'price')