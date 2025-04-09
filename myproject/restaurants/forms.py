from django import forms

from myproject.restaurants.models import Restaurant


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        exclude = ('account', "rating", "discount")