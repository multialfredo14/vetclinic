from django.contrib import admin
from django.utils.html import format_html
from .models import Product, StockMovement


class StockMovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("reason", "quantity", "performed_by", "notes", "created_at")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "product_type", "unit", "stock", "min_stock", "stock_status", "expiration")
    list_filter = ("product_type", "expiration")
    search_fields = ("name", "lot")
    readonly_fields = ("created_at", "updated_at")
    inlines = [StockMovementInline]
    fieldsets = (
        ("Producto", {"fields": ("name", "product_type", "unit", "notes")}),
        ("Stock", {"fields": ("stock", "min_stock")}),
        ("Lote / Caducidad", {"fields": ("lot", "expiration")}),
        ("Metadatos", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Estado")
    def stock_status(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color:red;font-weight:bold;">⚠ Bajo</span>')
        return format_html('<span style="color:green;">OK</span>')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "reason", "quantity", "performed_by", "created_at")
    list_filter = ("reason", "created_at")
    search_fields = ("product__name", "performed_by__username")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("product", "performed_by")
