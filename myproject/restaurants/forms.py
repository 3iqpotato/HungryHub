from django import forms

from myproject.restaurants.models import Restaurant


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        exclude = ('account', "rating", "discount")

class RestaurantEditForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'img', 'phone_number', 'address', 'discount']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'img': forms.FileInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'img': 'Restaurant Image',
            'discount': 'Discount (%)'
        }