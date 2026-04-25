from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("inventory/", views.ProductListView.as_view(), name="product_list"),
    path("inventory/new/", views.ProductCreateView.as_view(), name="product_create"),
    path("inventory/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("inventory/movement/", views.StockMovementCreateView.as_view(), name="stock_movement"),
]
