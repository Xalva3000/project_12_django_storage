from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from .utils import DataMixin
from .models import Product
from .forms import AddProductForm


def index(request):
    return render(request, 'products/home.html')


class ProductsList(DataMixin, ListView):
    template_name = 'products/products.html'
    context_object_name = 'products'
    # allow_empty = False
    title_page = 'Продукты'
    category_page = 'products'
    paginate_by = 20

    def get_queryset(self):
        return Product.objects.all()


class AddProduct(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddProductForm
    template_name = 'products/add_product.html'
    title_page = 'Добавление продукта'
    category_page = 'products'
    success_url = reverse_lazy('products:products')

    # def get_success_url(self):
    #     pk = self.kwargs["pk"]
    #     return reverse('products:product', kwargs={"pk": pk})

class UpdateProduct(LoginRequiredMixin, DataMixin, UpdateView):
    model = Product
    fields = ['fish', 'cutting', 'size', 'producer', 'package',
              'fixed_weight', 'weight']
    template_name = 'products/add_product.html'
    # success_url = reverse_lazy('products:product')
    title_page = 'Редактирование продукта'
    category_page = 'products'

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse('products:product', kwargs={"pk": pk})


class ShowProduct(LoginRequiredMixin, DataMixin, DetailView):
    model = Product
    template_name = 'products/product.html'
    context_object_name = 'product'
    pk_url_kwarg = 'pk'
    title_page = 'Детали продукта'
    category_page = 'products'

    def get_object(self, queryset=None):
        return get_object_or_404(Product.objects, pk=self.kwargs[self.pk_url_kwarg])


def about(request: HttpRequest):
    return render(request, 'products/about.html')