from django.db import models
from django.conf import settings


class Product(models.Model):
    TYPE_CHOICES = [
        ("medicine", "Medicamento"),
        ("vaccine", "Vacuna"),
        ("supply", "Insumo / Material"),
    ]
    name = models.CharField(max_length=150, verbose_name="Nombre")
    product_type = models.CharField(max_length=15, choices=TYPE_CHOICES, verbose_name="Tipo")
    unit = models.CharField(max_length=30, verbose_name="Unidad de medida")
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Stock actual")
    min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Stock mínimo (alerta)")
    lot = models.CharField(max_length=50, blank=True, verbose_name="Lote")
    expiration = models.DateField(null=True, blank=True, verbose_name="Caducidad")
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_product_type_display()})"

    @property
    def is_low_stock(self):
        return self.stock <= self.min_stock


class StockMovement(models.Model):
    REASON_CHOICES = [
        ("purchase", "Compra / Entrada"),
        ("vaccination", "Vacunación aplicada"),
        ("prescription", "Dispensación en receta"),
        ("adjustment", "Ajuste manual"),
        ("expiry", "Baja por caducidad"),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="movements", verbose_name="Producto")
    reason = models.CharField(max_length=15, choices=REASON_CHOICES, verbose_name="Motivo")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad (+/-)")
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        null=True, blank=True, verbose_name="Realizado por",
    )
    reference_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID de referencia")
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento de stock"
        verbose_name_plural = "Movimientos de stock"
        ordering = ["-created_at"]

    def __str__(self):
        sign = "+" if self.quantity >= 0 else ""
        return f"{self.product} {sign}{self.quantity} ({self.get_reason_display()})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.stock = models.F("stock") + self.quantity
        self.product.save(update_fields=["stock"])
        self.product.refresh_from_db()
