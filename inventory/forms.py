from django import forms
from .models import Product, StockMovement


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "product_type", "unit", "stock", "min_stock", "lot", "expiration", "notes")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "product_type": forms.Select(attrs={"class": "form-select"}),
            "unit": forms.TextInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "min_stock": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "lot": forms.TextInput(attrs={"class": "form-control"}),
            "expiration": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lot"].required = False
        self.fields["expiration"].required = False
        self.fields["notes"].required = False


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ("product", "reason", "quantity", "notes")
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "reason": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["notes"].required = False
