from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from accounts.mixins import RoleRequiredMixin
from .forms import ProductForm, StockMovementForm
from .models import Product, StockMovement


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "inventory/product_list.html"
    context_object_name = "products"
    paginate_by = 30

    def get_queryset(self):
        qs = Product.objects.all()
        q = self.request.GET.get("q", "").strip()
        ptype = self.request.GET.get("type", "")
        low = self.request.GET.get("low", "")
        if q:
            qs = qs.filter(name__icontains=q)
        if ptype:
            qs = qs.filter(product_type=ptype)
        if low:
            from django.db.models import F
            qs = qs.filter(stock__lte=F("min_stock"))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        ctx["type_filter"] = self.request.GET.get("type", "")
        ctx["low_filter"] = self.request.GET.get("low", "")
        ctx["type_choices"] = Product.TYPE_CHOICES
        ctx["low_stock_count"] = Product.objects.filter(
            stock__lte=0
        ).count()
        return ctx


class ProductCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Admin"]
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form.html"
    success_url = reverse_lazy("inventory:product_list")

    def form_valid(self, form):
        messages.success(self.request, f"Producto '{form.instance.name}' creado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, title="Nuevo producto")


class ProductUpdateView(RoleRequiredMixin, UpdateView):
    allowed_roles = ["Admin"]
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form.html"
    success_url = reverse_lazy("inventory:product_list")

    def form_valid(self, form):
        messages.success(self.request, "Producto actualizado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, title=f"Editar: {self.object.name}")


class StockMovementCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = ["Admin"]
    model = StockMovement
    form_class = StockMovementForm
    template_name = "inventory/movement_form.html"
    success_url = reverse_lazy("inventory:product_list")

    def form_valid(self, form):
        form.instance.performed_by = self.request.user
        messages.success(self.request, "Movimiento de stock registrado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs, title="Registrar movimiento de stock")
