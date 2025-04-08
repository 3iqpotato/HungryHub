from django import forms

from myproject.suppliers.models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        exclude = ('account',)