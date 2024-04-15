from django.urls import path
from . import views
from . import execution


urlpatterns = [
    path("", views.ContractsMinimalList.as_view(), name='contracts'),
    path("plus/", views.ContractsPlusList.as_view(), name='contracts_plus'),
    path("deleted/", views.DeletedContractsMinimalList.as_view(), name='contracts_deleted'),
    path("add_contract/", views.AddContract.as_view(), name='add_contract'),
    path("<int:pk>/", views.ShowContract.as_view(), name='contract'),
    path("<int:pk>/update/", views.UpdateContract.as_view(), name='contract_update'),
    path('<int:pk>/add_specifications/',  views.add_specifications, name='add_specifications'),
    path('<int:pk>/reserve/', execution.switch_reserve_by_contract_id, name='contract_reserve'),
    path('<int:pk>/payment/', execution.switch_payment_by_contract_id, name='contract_payment'),
    path('<int:pk>/execute/', execution.switch_execution_by_contract_id, name='contract_execution'),
    path('<int:pk>/delete/', execution.delete_contract, name='contract_delete'),
    path('<int:pk>/change_manager_share/', views.change_manager_share, name='change_manager_share'),
    path('<int:pk>/change_note/', views.change_note, name='change_note'),
    path('<int:pk>/add_payment/', views.add_payment, name='add_payment'),
    # path("add_contract/", views.add_contract, name='add_contract'),
]


