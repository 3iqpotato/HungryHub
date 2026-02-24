from django import forms

from myproject.suppliers.models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        exclude = ('account', 'status', "daily_earnings", "last_reset",)


class SupplierProfileForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'img', 'phone_number', 'type']

        widgets = {
            'img': forms.FileInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
        }