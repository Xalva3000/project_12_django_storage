from copy import deepcopy


menu = [{'title': "Продукты", 'url_name': 'products:products'},
        {'title': "Контрагенты", 'url_name': 'contractors:contractors'},
        {'title': "Контракты", 'url_name': 'contracts:contracts'},
		{'title': "Склад", 'url_name': 'storage_items:storage_items'},
		# {'title': "Счет", 'url_name': 'contact'},
]

tools = {
	"products": [{'title': "Список", 'path': 'products/'},
	             {'title': "Добавить", 'path': 'products/add_product/'}, ],
	"contractors": [{'title': "Список", 'path': 'contractors/'},
	                {'title': "Добавить", 'path': 'contractors/add_contractor/'},],
	"contracts": [{'title': 'Список', 'path': 'contracts'},
	              {'title': "Список+", 'path': 'contracts/plus/'},
	              {'title': "Добавить", 'path': 'contracts/add_contract/'},
	              {'title': "Удаленные", 'path': 'contracts/deleted/'},],
	"storage_items": [{'title': 'Список', 'path': 'storage_items/storage_items/'},],
}


class DataMixin:
	title_page = None
	category_page = None
	menu_selected = None
	tool_selected = None
	extra_context: dict[str, str | int] = {}

	def __init__(self):
		if self.title_page:
			self.extra_context['title'] = self.title_page
		if self.menu_selected is not None:
			self.extra_context['menu_selected'] = self.menu_selected
		if self.tool_selected is not None:
			self.extra_context['tool_selected'] = self.tool_selected

	def get_mixin_context(self, context, **kwargs):
		# context['menu'] = menu
		if self.category_page:
			context['tools'] = tools[self.category_page]
		context['custom_url'] = self.cut_page_from_url(self.request.get_full_path())
		context.update(kwargs)
		return context

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		return self.get_mixin_context(context)

	@staticmethod
	def cut_page_from_url(string):
		if 'page' in string:
			return string.rsplit('page', 1)[0]
		elif '?' in string:
			return string + '&'
		else:
			return '?'

#
# def contract_rpe_map(contract):
# 	return ''.join(map(lambda b: str(int(b)), [contract.reserved, contract.paid, contract.executed]))


def contract_re_map(contract):
	return ''.join(map(lambda b: str(int(b)), [contract.reserved, contract.executed]))

def contract_rpe_map(contract):
	return ''.join(map(lambda b: str(int(b)), [contract.reserved, contract.executed, contract.paid]))