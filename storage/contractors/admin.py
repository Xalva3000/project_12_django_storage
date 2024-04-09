from django.contrib import admin

from .models import Contractor


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'date_create',)
	list_display_links = ('name',)
	ordering = ['name', 'id']
	list_per_page = 8
	search_fields = ['name', 'address',]