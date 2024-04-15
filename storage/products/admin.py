from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'fish', 'cutting', 'size',
		'producer', 'package', 'date_create')
	list_display_links = ('fish',)
	# list_editable = (
	# 	'cutting', 'size', 'producer', 'package',
	# 	'weight', 'fixed_weight')
	ordering = ['fish', 'cutting', 'size', 'producer', 'date_create']
	list_per_page = 8
	search_fields = ['fish', 'cutting', 'size']